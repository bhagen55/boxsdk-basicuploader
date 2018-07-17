pyinstaller --noconfirm --log-level=WARN ^
    --onefile --windowed ^
    --hidden-import=PyQt5.sip ^
    --icon=.\assetuploader_icon.ico ^
    AssetUploader.spec