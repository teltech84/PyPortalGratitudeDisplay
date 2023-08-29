import dropbox
import os

dbx =dropbox.Dropbox("COPYKEYGENERATEDFROMDROPBOXAPPHERE")
for entry in dbx.files_list_folder('').entries:
    print(entry.name)

if os.path.exists(os.getcwd() + "/presently-backup.csv"):
    os.remove(os.getcwd() + "/presently-backup.csv")
    print("The file has been deleted successfully")

#local_file_path = os.getcwd() + "/presently-backup.csv"
#with open(local_file_path, 'wb') as f:
#    metadata, result = dbx.files_download(path="/Apps/PresentlyBackups/presently-backup.csv")
#    f.write(result.content)

dbx.files_download_to_file('presently-backup.csv','/Apps/PresentlyBackups/presently-backup.csv')
