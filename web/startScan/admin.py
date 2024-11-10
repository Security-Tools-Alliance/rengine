from django.contrib import admin
from startScan.models import *

admin.site.register(ScanHistory)
admin.site.register(SubScan)
admin.site.register(Subdomain)
admin.site.register(ScanActivity)
admin.site.register(EndPoint)
admin.site.register(Vulnerability)
admin.site.register(CweId)
admin.site.register(CveId)
admin.site.register(VulnerabilityReference)
admin.site.register(VulnerabilityTags)
admin.site.register(Port)
admin.site.register(IpAddress)
admin.site.register(DirectoryFile)
admin.site.register(DirectoryScan)
admin.site.register(Technology)
admin.site.register(MetaFinderDocument)
admin.site.register(Email)
admin.site.register(Employee)
admin.site.register(Dork)
admin.site.register(Waf)
admin.site.register(CountryISO)
admin.site.register(Command)
admin.site.register(LLMVulnerabilityReport)
admin.site.register(S3Bucket)
