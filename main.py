import boxsdk
from boxsdk.exception import BoxAPIException
import json
import os
from pathlib import Path
import logging

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Base filepath for uploads
upload_folder = "./upload"

# Get authorization info and authenticate
def authenticate():
	with open('./keys/appauth.json') as f:
		auth_info = json.load(f)

	with open('./keys/privkey','w') as f:
		f.write(auth_info["boxAppSettings"]["appAuth"]["privateKey"])

	# Authentication info (using oauth)
	auth = boxsdk.JWTAuth(
		client_id=auth_info["boxAppSettings"]["clientID"],
		client_secret=auth_info["boxAppSettings"]["clientSecret"],
		enterprise_id=auth_info["enterpriseID"],
		jwt_key_id=auth_info["boxAppSettings"]["appAuth"]["publicKeyID"],
		rsa_private_key_file_sys_path="./keys/privkey", #TODO: Pull key automatically or at least do file checking
		rsa_private_key_passphrase=auth_info['boxAppSettings']['appAuth']['passphrase'].encode("ascii")
	)

	# Authenticate
	access_token = auth.authenticate_instance()
	client = boxsdk.Client(auth)

	# Get user info
	me = client.user(user_id='me').get()
	logger.info('User Login: ' + me['login'])
	#print(colored("[Info] ", 'blue') + 'User Login: ' + me['login'])

	return client


# Create a folder
def create_folder(base_folder, folder_name):
	folder = None
	try:
		folder = base_folder.create_subfolder(folder_name)
	except BoxAPIException:
		print("Error creating folder " + folder_name)


def get_folder_contents(folder_id):
	folder = get_folder(folder_id)
	items = folder.get_items(limit=100, offset=0)


# Uploads file to given folder ID
# Returns dict with file ID and direct download URL
# If file already exists, returns information of existing file
def upload(dest_folder_id, filename):
	to_upload = Path(upload_folder + "/" + filename)
	dest_folder = client.folder(dest_folder_id).get()

	file_info = {'id':'', 'url':''}

	try:
		uploaded_file = dest_folder.upload(to_upload, filename, preflight_check = True)
	except BoxAPIException as ex:
		if ex.code == "item_name_in_use":
			logger.warning("Item name \"" + ex.context_info['conflicts']['name'] + "\" already in use. Supplying existing item information.")
			#print(colored("[Warning] ", 'yellow') + "Item name \"" + ex.context_info['conflicts']['name'] + "\" already in use. Supplying existing item information.")
			file_info['id'] = ex.context_info['conflicts']['id']
			file_info['url'] = client.file(file_info['id']).get_shared_link_download_url()
		else:
			print(colored("[Error] ", 'red') +  ex.code)
	else:
		direct_link = uploaded_file.get_shared_link_download_url()

		file_info['id'] = uploaded_file.object_id
		file_info['url'] = direct_link;
		logger.info("Item " + filename + " uploaded successfully.")
		#print(colored("[Info] ", 'green') + "Item " + filename + " uploaded successfully.")

	return(file_info)


def delete_folder(id):
	delete(client.folder(id).get())


def delete_file(id):
	delete(client.file(id).get())


def delete(item):
	try:
		item.delete()
	except:
		pass
	else:
		print(colored("[Info] ", 'green') + "Item " + item.name + "deleted successfully.")
	return True;


if __name__ == '__main__':
	client = authenticate()

	print(delete_file('303640799233'))
