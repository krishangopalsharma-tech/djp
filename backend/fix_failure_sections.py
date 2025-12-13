import os
import django
import sys

# Setup Django environment
sys.path.append('/home/adi/djp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rfms.settings')
django.setup()

from failures.models import Failure

def fix_missing_sections():
    print("Checking for failures with missing sections...")
    
    # query failures where section is null but sub_section is NOT null
    failures = Failure.objects.filter(section__isnull=True, sub_section__isnull=False)
    
    count = failures.count()
    print(f"Found {count} failures with missing section but valid sub_section.")
    
    if count == 0:
        print("No fixes needed.")
        return

    updated_count = 0
    for failure in failures:
        if failure.sub_section and failure.sub_section.section:
            print(f"Updating Failure #{failure.fail_id}: {failure.sub_section.name} -> {failure.sub_section.section.name}")
            failure.section = failure.sub_section.section
            failure.save(update_fields=['section'])
            updated_count += 1
        else:
            print(f"Skipping Failure #{failure.fail_id}: SubSection {failure.sub_section.name if failure.sub_section else 'None'} has no parent Section.")

    print(f"Successfully updated {updated_count} failures.")

if __name__ == "__main__":
    fix_missing_sections()
