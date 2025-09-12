import os
import shutil
from pathlib import Path

def copy_shared_files():
    # Get the root directory of the project
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    
    # Path to the shared files
    shared_dir = current_dir / "services" / "shared"
    
    # Get all directories in the services folder
    services_dir = current_dir / "services"
    service_dirs = [d for d in services_dir.iterdir() if d.is_dir() and d.name != "shared"]
    
    # Print the services found
    print(f"Found {len(service_dirs)} services: {[s.name for s in service_dirs]}")
    
    # Copy files to each service
    for service_dir in service_dirs:
        # Path to the app folder in the service
        app_dir = service_dir / "app"
        
        # Check if the app directory exists
        if not app_dir.exists():
            print(f"Warning: app directory doesn't exist in {service_dir.name}. Skipping...")
            continue
        
        # Create _shared directory if it doesn't exist
        shared_target_dir = app_dir
        shared_target_dir.mkdir(exist_ok=True)
        
        print(f"\nCopying shared files to {service_dir.name}/app...")
        
        # Copy each file from shared to app/_shared
        for file_path in shared_dir.glob("*"):
            if file_path.is_file():
                # Destination path
                dest_path = shared_target_dir / file_path.name
                
                # Copy the file
                shutil.copy2(file_path, dest_path)
                print(f"  Copied: {file_path.name} -> {dest_path}")
    
    print("\nAll shared files have been copied to each service's app directory.")

if __name__ == "__main__":
    copy_shared_files()
