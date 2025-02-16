from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from .models import Subdomain, IpAddress
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@receiver(pre_delete, sender=Subdomain)
def handle_subdomain_deletion(sender, instance, **kwargs):
    """Cleanup orphaned IPs after subdomain deletion."""
    try:
        ips_to_check = list(instance.ip_addresses.all())
        logger.info(f"Checking IPs associated with subdomain {instance.name}")
        
        def post_deletion_cleanup():
            """Callback executed after transaction validation."""
            for ip in ips_to_check:
                # Final check after complete deletion
                if not Subdomain.objects.filter(ip_addresses=ip).exists():
                    logger.warning(f"Deleting orphaned IP {ip.address}")
                    ip.delete()
                else:
                    logger.info(f"IP {ip.address} still in use")
        
        # Defer the check after the transaction
        transaction.on_commit(post_deletion_cleanup)
        
    except Exception as e:
        logger.error(f"Error during post-deletion cleanup: {str(e)}")

@receiver(m2m_changed, sender=Subdomain.ip_addresses.through)
def handle_subdomain_ip_changes(sender, instance, action, pk_set, **kwargs):
    """Handle cleanup when IPs are removed from a subdomain."""
    if action == "post_remove" and pk_set:
        try:
            with transaction.atomic():
                removed_ips = IpAddress.objects.filter(id__in=pk_set)
                for ip in removed_ips:
                    if not Subdomain.objects.filter(ip_addresses=ip).exists():
                        logger.warning(f"Deleting orphaned IP {ip.address} after M2M change")
                        ip.delete()
        except Exception as e:
            logger.error(f"Error during M2M IP cleanup: {str(e)}")
