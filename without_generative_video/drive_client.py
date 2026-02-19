# drive_client.py - FIXED VERSION (no tuple bug)
import os
import io
import pickle
import shutil
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Get authenticated Google Drive service"""
    creds = None
    token_file = 'token.pickle'
    
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def download_property_folder(folder_id: str, output_dir: str):
    """
    Download files from property folders.
    folder_id: The InputProperties folder ID
    """
    service = get_drive_service()
    
    print(f"\n📥 Downloading from: {folder_id}")
    
    # 1. Get the InputProperties folder info
    try:
        parent_folder = service.files().get(
            fileId=folder_id,  # ← FIXED: No tuple!
            fields='id, name'
        ).execute()
        print(f"📁 Parent folder: {parent_folder['name']}")
    except Exception as e:
        print(f"❌ Cannot access folder: {e}")
        raise
    
    # 2. List property folders inside
    query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    results = service.files().list(
        q=query,
        fields='files(id, name)',
        pageSize=10
    ).execute()
    
    prop_folders = results.get('files', [])
    
    if not prop_folders:
        raise RuntimeError("No property folders found")
    
    print(f"📂 Found {len(prop_folders)} property folders:")
    for folder in prop_folders:
        print(f"  • {folder['name']}")
    
    # Use the FIRST property folder
    prop_folder = prop_folders[0]
    prop_id = prop_folder['id']
    prop_name = prop_folder['name']
    
    print(f"\n🔍 Processing: {prop_name}")
    
    # 3. List files in the property folder
    query = f"'{prop_id}' in parents"
    results = service.files().list(
        q=query,
        fields='files(id, name, mimeType)',
        pageSize=50
    ).execute()
    
    files = results.get('files', [])
    
    if not files:
        raise RuntimeError(f"No files found in {prop_name}")
    
    print(f"📄 Found {len(files)} files:")
    for file in files:
        print(f"  • {file['name']} ({file.get('mimeType', 'unknown')})")
    
    # 4. Create output directory
    prop_output_dir = os.path.join(output_dir, prop_name)
    if os.path.exists(prop_output_dir):
        shutil.rmtree(prop_output_dir)  # Clear old files
    os.makedirs(prop_output_dir, exist_ok=True)
    
    print(f"\n💾 Downloading to: {prop_output_dir}")
    
    # 5. Download files
    assets = []
    config_path = None
    
    for file in files:
        file_id = file["id"]
        name = file["name"]
        mime = file.get("mimeType", "")
        
        local_path = os.path.join(prop_output_dir, name)
        
        print(f"  ⬇️  {name}")
        
        try:
            # Download file
            request = service.files().get_media(fileId=file_id)
            
            with open(local_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            
            print(f"    ✅ Downloaded")
            
            # Check file type
            if name.lower() == "config.json":
                config_path = local_path
            elif mime.startswith("image/") or mime.startswith("video/"):
                assets.append(local_path)
                
        except Exception as e:
            print(f"    ❌ Failed: {str(e)[:80]}")
    
    if not config_path:
        # Look for any JSON file
        for file in files:
            if file['name'].lower().endswith('.json'):
                config_path = os.path.join(prop_output_dir, file['name'])
                print(f"✅ Using {file['name']} as config file")
                break
    
    if not config_path:
        raise RuntimeError("No config file found")
    
    print(f"\n✅ SUCCESS!")
    print(f"   Downloaded {len(assets)} assets")
    print(f"   Config: {os.path.basename(config_path)}")
    
    return assets, config_path

def upload_video(file_path: str, folder_id: str) -> str:
    """Upload video to Drive"""
    service = get_drive_service()
    
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id],
    }
    
    media = MediaFileUpload(file_path, mimetype='video/mp4')
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    
    file_id = uploaded["id"]
    return f"https://drive.google.com/file/d/{file_id}/view"