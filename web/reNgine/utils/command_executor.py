"""
Command execution framework with unified streaming/buffering interface
"""

import contextlib
import re
import time
import select
import subprocess
import logging
from django.utils import timezone
from django.apps import apps
import shlex
import json
import os

logger = logging.getLogger(__name__)

class CommandExecutor:
    """Unified command execution handler with streaming capabilities"""
    
    def __init__(self, cmd, context=None):
        self.cmd = cmd
        self.context = context or {}
        self.process = None
        self.command_obj = None
        self.output_buffer = []
        self.return_code = -1
        self.timeout = self._calculate_timeout()
        self.trunc_char = self.context.get('trunc_char')
        self.is_json = '-json' in cmd
        self.dry_run = os.getenv('COMMAND_EXECUTOR_DRY_RUN', '0') == '1'

    def execute(self, stream=False):
        """Main execution entry point"""
        if self.dry_run:
            logger.debug(f'[DRY RUN] Would execute command: {self.cmd}')
            return self._mock_execution()
        
        logger.debug(f"🔧 Starting command execution in {'STREAM' if stream else 'BUFFER'} mode")
        logger.debug(f"🔧 Command: {self.cmd}")
        logger.debug(f"🔧 Context: {self.context}")
        self._pre_execution_setup()
        
        try:
            return self._handle_execution(stream)
        except Exception as e:
            logger.error(f"🔥 Critical execution error: {str(e)}", exc_info=True)
            self._handle_execution_error(e)
        finally:
            if not stream:
                self._post_execution_cleanup()
        
        return self._finalize_output(stream)

    def _get_command_model(self):
        return apps.get_model('startScan', 'Command')

    def _calculate_timeout(self):
        """Determine timeout based on command type"""
        return 3600 if 'nuclei' in self.cmd.lower() else 1800

    def _pre_execution_setup(self):
        """Prepare execution environment"""
        logger.info(f"Initializing command execution: {self.cmd}")
        Command = self._get_command_model()
        self.command_obj = Command.objects.create(
            command=self.cmd,
            time=timezone.now(),
            scan_history_id=self.context.get('scan_id'),
            activity_id=self.context.get('activity_id')
        )

    def _handle_execution(self, stream):
        """Core execution logic"""
        self.process = self._launch_process()

        try:
            result = self._stream_output() if stream else self._buffer_output()
        finally:
            self._save_return_code()

        return result

    def _launch_process(self):
        """Launch subprocess with improved security"""
        if self.dry_run:
            logger.info(f'📄 [DRY RUN] Skipping process launch for: {self.cmd}')
            return None

        logger.debug("🚀 Launching process")

        if self.context.get('shell', False):
            # When shell is required, log a warning for security auditing
            logger.warning(f"Using shell=True for command execution (security risk): {self.cmd}")
            process = subprocess.Popen(
                self.cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.context.get('cwd'),
                encoding=self.context.get('encoding', 'utf-8'),
                errors='replace'
            )
        else:
            # Preferred: using list mode for better security
            cmd_args = shlex.split(self.cmd) if isinstance(self.cmd, str) else self.cmd
            process = subprocess.Popen(
                cmd_args,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.context.get('cwd'),
                encoding=self.context.get('encoding', 'utf-8'), 
                errors='replace'
            )

        logger.debug(f"📝 Process launched with PID: {process.pid}")
        return process

    def _stream_output(self):
        """Stream output line by line"""
        logger.debug("🔌 Starting stream output")
        for line in self._read_process_output():
            if isinstance(line, dict):
                self._update_command_object(json.dumps(line), is_stream=True)
            else:
                self._update_command_object(line, is_stream=True)
            yield line

    def _buffer_output(self):
        """Collect all output before returning"""
        logger.debug("📦 Starting buffer output")
        try:
            return self._extracted_from__buffer_output()
        except Exception as e:
            logger.error(f"🔥 Buffer processing failed: {str(e)}")
            return self.process.returncode, ''

    def _extracted_from__buffer_output(self):
        # Wait for process completion and get output
        stdout, stderr = self.process.communicate()

        # Decode output
        output = stdout.decode('utf-8', errors='replace') if stdout else ''
        error_output = stderr.decode('utf-8', errors='replace') if stderr else ''

        # Log and save full output
        full_output = output + error_output
        if full_output:
            logger.debug(f"📥 Raw buffer data:\n{full_output}")
            self._update_command_object(full_output, is_stream=False)
        else:
            logger.debug("📭 No output to save")

        # Split into lines for processing
        output_lines = full_output.split('\n')
        logger.debug(f"📦 Buffer line count: {len(output_lines)}")

        return self.process.returncode, full_output

    def _read_process_output(self):
        """Read process output with timeout handling"""
        logger.debug("📖 Starting process output reading")
        while True:
            ready, _, _ = select.select([self.process.stdout, self.process.stderr], [], [], 1.0)

            if not ready:
                if self.process.poll() is not None:
                    logger.debug("⏹ Process finished")
                    break
                self._check_timeout()
                continue

            raw_line = self._read_ready_stream(ready)
            logger.debug(f"📥 Raw line from stream: {raw_line or None}...")

            if raw_line:
                line = self._process_line(raw_line)

                if self.is_json:
                    try:
                        # Improved JSON handling with error recovery
                        json_buffer = ''
                        if isinstance(line, bytes):
                            line = line.decode('utf-8', errors='replace').strip()
                        else:
                            line = line.strip()

                        if not line:
                            continue

                        # Attempt to parse as complete JSON
                        with contextlib.suppress(json.JSONDecodeError):
                            yield json.loads(line)
                            continue
                        # Handle concatenated JSON objects or partial content
                        json_buffer += line
                        decoder = json.JSONDecoder()
                        while json_buffer:
                            try:
                                obj, idx = decoder.raw_decode(json_buffer)
                                yield obj
                                json_buffer = json_buffer[idx:].lstrip()
                            except json.JSONDecodeError:
                                if len(json_buffer) > 1024:  # Prevent infinite loop
                                    logger.warning(f"Truncating malformed JSON buffer: {json_buffer[:200]}...")
                                    json_buffer = ''
                                break

                    except Exception as e:
                        logger.error(f"❌ JSON processing failed: {str(e)}")
                        logger.debug(f"❌ Problematic content: {line[:200]}...")
                else:
                    logger.debug("📝 Yielding text line")
                    yield line
            elif self.process.poll() is not None:
                break

    def _check_timeout(self):
        """Check and handle execution timeout"""
        if time.time() - self.command_obj.time.timestamp() > self.timeout:
            self._terminate_process()
            raise TimeoutError(f"Command timeout after {self.timeout} seconds")

    def _process_line(self, line):
        """Process individual output line"""
        logger.debug(f"📥 Processing raw line: {line[:100]}...")

        # Final ANSI cleanup
        line = re.sub(r'\x1b\[[0-9;]*[mGKH]', '', line)

        # Truncation logic
        if self.trunc_char and len(line) > self.trunc_char:
            truncated = f'{line[:self.trunc_char]}...'
            logger.debug(f"✂️ Truncated from {len(line)} to {len(truncated)} chars")
            line = truncated

        processed = line.strip()
        logger.debug(f"✅ Processed line: {processed[:100]}...")
        return processed

    def _read_ready_stream(self, ready):
        """Read from ready stream with error handling"""
        try:
            # Read binary data directly
            raw_data = b''
            for stream in ready:
                if stream in [self.process.stdout, self.process.stderr]:
                    raw_data += os.read(stream.fileno(), 4096)
            if not raw_data:
                logger.debug("📭 No data in stream")
                return None

            logger.debug(f"🔠 Raw binary data: {raw_data[:200]}...")

            # Decode with error handling
            decoded = raw_data.decode('utf-8', errors='replace')
            logger.debug(f"📖 Decoded data: {decoded[:200]}...")

            return decoded

        except Exception as e:
            logger.error(f"🚨 Stream read failed: {str(e)}")
            return None

    def _update_command_object(self, data, is_stream=False):
        """Update command object in database with proper output handling"""
        if not self.command_obj:
            return

        try:
            logger.debug("💾 Updating command object table with data...")
            # Force string type for output field
            current_output = self.command_obj.output or ''

            # Buffer mode: direct assignment
            if not is_stream:
                logger.debug(f"📦 Saving buffer output ({len(data)} chars)")
                self._extracted_from__update_command_object(
                    current_output,
                    data,
                    "✅ Command object updated successfully with buffer mode",
                )
                return

            # Stream mode: handle JSON properly
            logger.debug(f"🔁 Appending stream data: {str(data)[:100]}...")

            if isinstance(data, dict):  # Already parsed JSON
                output_line = json.dumps(data) + '\n'
            else:
                output_line = f"{data}\n"

            self._extracted_from__update_command_object(
                current_output,
                output_line,
                "✅ Command object updated successfully with stream mode",
            )
        except Exception as e:
            logger.error(f"❌ Output update failed: {str(e)}")
            self.command_obj.output = f"Error: {str(e)}"
            self.command_obj.save(update_fields=['output'])

    def _extracted_from__update_command_object(self, current_output, arg1, arg2):
        self.command_obj.output = current_output + arg1
        self.command_obj.save(update_fields=['output'])
        logger.debug(arg2)

    def _handle_execution_error(self, error):
        """Handle execution errors"""
        logger.error(f"Command execution failed: {str(error)}")
        self.command_obj.error_output = str(error)
        self.command_obj.save()

    def _terminate_process(self):
        """Terminate running process"""
        if self.process.poll() is None:
            self.process.terminate()
            time.sleep(5)
            if self.process.poll() is None:
                self.process.kill()

    def _post_execution_cleanup(self):
        """Cleanup resources after execution"""
        self.process.wait()
        
        remaining_output, remaining_error = self.process.communicate()
        if remaining_output:
            self.output_buffer.append(remaining_output)
        if remaining_error:
            logger.debug(f"Remaining stderr: {remaining_error}")
        
        self.return_code = self.process.returncode
        self._finalize_command_object()
        self._write_execution_history()

    def _finalize_command_object(self):
        """Final updates to command object"""
        self.command_obj.return_code = self.return_code
        self.command_obj.save()

    def _write_execution_history(self):
        """Write execution history if needed"""
        if history_file := self.context.get('history_file'):
            with open(history_file, 'a') as f:
                f.write(f'\n{self.cmd}\n{self.return_code}\n{self.output_buffer}\n------------------\n')

    def _finalize_output(self, stream):
        """Return appropriate output format"""
        if stream:
            return self._stream_output()
        return self.return_code, ''.join(self.output_buffer)

    def _save_return_code(self):
        """Persist return code to database"""
        if self.process and self.command_obj:
            try:
                # Wait for process termination if still running
                if self.process.poll() is None:
                    logger.debug("⏳ Process still running - waiting for completion")
                    self.process.wait()
                
                return_code = self.process.returncode
                self.command_obj.return_code = return_code
                self.command_obj.save(update_fields=['return_code'])
                logger.debug(f"💾 Saved return code: {return_code}")
                
            except Exception as e:
                logger.error(f"❌ Failed to save return code: {str(e)}")
                self.command_obj.return_code = -1
                self.command_obj.save(update_fields=['return_code'])

    def _mock_execution(self):
        """Generate mock command output for dry runs"""
        mock_data = {
            'command': self.cmd,
            'output': f"DRY RUN OUTPUT FOR: {self.cmd}",
            'return_code': 0
        }

        return json.dumps(mock_data) if self.is_json else mock_data

def stream_command(cmd, **kwargs):
    context = {
        'shell': kwargs.get('shell', False),
        'cwd': kwargs.get('cwd'),
        'history_file': kwargs.get('history_file'),
        'scan_id': kwargs.get('scan_id'),
        'activity_id': kwargs.get('activity_id'),
        'encoding': kwargs.get('encoding', 'utf-8'),
        'trunc_char': kwargs.get('trunc_char'),
        'dry_run': kwargs.get('dry_run', os.getenv('COMMAND_EXECUTOR_DRY_RUN', '0') == '1')
    }
    executor = CommandExecutor(cmd, context)
    return executor.execute(stream=True)

def run_command(cmd, **kwargs):
    context = {
        'shell': kwargs.get('shell', False),
        'cwd': kwargs.get('cwd'),
        'history_file': kwargs.get('history_file'),
        'scan_id': kwargs.get('scan_id'),
        'activity_id': kwargs.get('activity_id'),
        'remove_ansi': kwargs.get('remove_ansi_sequence', False),
        'encoding': kwargs.get('encoding', 'utf-8'),
        'trunc_char': kwargs.get('trunc_char'),
        'dry_run': kwargs.get('dry_run', os.getenv('COMMAND_EXECUTOR_DRY_RUN', '0') == '1')
    }
    executor = CommandExecutor(cmd, context)
    return executor.execute(stream=False)
