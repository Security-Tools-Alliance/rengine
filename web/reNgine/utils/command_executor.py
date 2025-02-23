"""
Command execution framework with unified streaming/buffering interface
"""
import re
import time
import select
import subprocess
import logging
from django.utils import timezone
from startScan.models import Command
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

    def execute(self, stream=False):
        """Main execution entry point"""
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

    def _calculate_timeout(self):
        """Determine timeout based on command type"""
        return 3600 if 'nuclei' in self.cmd.lower() else 1800

    def _pre_execution_setup(self):
        """Prepare execution environment"""
        logger.info(f"Initializing command execution: {self.cmd}")
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
            if stream:
                result = self._stream_output()
            else:
                result = self._buffer_output()
        finally:
            self._save_return_code()
        
        return result

    def _launch_process(self):
        """Launch subprocess with proper command formatting"""
        logger.debug("🚀 Launching process")
        use_shell = self.context.get('shell', False)
        command = self.cmd if use_shell else shlex.split(self.cmd)
        
        return subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=use_shell,
            cwd=self.context.get('cwd'),
            encoding=None
        )

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
            
        except Exception as e:
            logger.error(f"🔥 Buffer processing failed: {str(e)}")
            return self.process.returncode, ''

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
            logger.debug(f"📥 Raw line from stream: {raw_line if raw_line else None}...")
            
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
                        try:
                            json_line = json.loads(line)
                            yield json_line
                            continue
                        except json.JSONDecodeError:
                            pass
                        
                        # Handle concatenated JSON objects or partial content
                        json_buffer += line
                        decoder = json.JSONDecoder()
                        while json_buffer:
                            try:
                                obj, idx = decoder.raw_decode(json_buffer)
                                yield obj
                                json_buffer = json_buffer[idx:].lstrip()
                            except json.JSONDecodeError as e:
                                if len(json_buffer) > 1024:  # Prevent infinite loop
                                    logger.warning(f"Truncating malformed JSON buffer: {json_buffer[:200]}...")
                                    json_buffer = ''
                                break
                        
                    except Exception as e:
                        logger.error(f"❌ JSON processing failed: {str(e)}")
                        logger.debug(f"❌ Problematic content: {line[:200]}...")
                        continue
                else:
                    logger.debug("📝 Yielding text line")
                    yield line
            else:
                if self.process.poll() is not None:
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
            truncated = line[:self.trunc_char] + '...'
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
                if stream == self.process.stdout:
                    raw_data += os.read(stream.fileno(), 4096)
                elif stream == self.process.stderr:
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
                self.command_obj.output = current_output + data
                self.command_obj.save(update_fields=['output'])
                logger.debug("✅ Command object updated successfully with buffer mode")
                return
                
            # Stream mode: handle JSON properly
            logger.debug(f"🔁 Appending stream data: {str(data)[:100]}...")
            
            if isinstance(data, dict):  # Already parsed JSON
                output_line = json.dumps(data) + '\n'
            else:
                output_line = f"{data}\n"
            
            self.command_obj.output = current_output + output_line
            self.command_obj.save(update_fields=['output'])
            logger.debug("✅ Command object updated successfully with stream mode")
            
        except Exception as e:
            logger.error(f"❌ Output update failed: {str(e)}")
            self.command_obj.output = f"Error: {str(e)}"
            self.command_obj.save(update_fields=['output'])

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