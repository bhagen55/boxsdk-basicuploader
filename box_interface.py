import boxsdk
from boxsdk.exception import BoxAPIException
import json
import os, errno
from pathlib import Path
import logging

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Base filepath for uploads
upload_folder_path = "./upload"
keys_folder_path = "./keys"


# Create base folder structure
def create_folders():
	folder_paths = [upload_folder_path, keys_folder_path]
	for path in folder_paths:
		try:
			 os.mkdir(path)
		except OSError as ex:
			if ex.errno == 17:
				logger.warning('Folder at ' + path + ' already exists.')
			else:
				raise


# Get authorization info and authenticate
# private key is automatically pulled from the .json file provided
# by box and saved to ./keys/privkey
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
		rsa_private_key_file_sys_path="./keys/privkey",
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


def get_folder_contents(folder_id):
	folder = get_folder(folder_id)
	items = folder.get_items(limit=100, offset=0)


# Creates a folder
# Returns the folder ID
def create_folder(base_folder_id, folder_name):
	try:
		new_folder = client.folder(base_folder_id).create_subfolder(folder_name)
		logger.info("Folder " + folder_name + " created successfully.")
		return new_folder.object_id
	except BoxAPIException as ex:
		if ex.code == "item_name_in_use":
			logger.warning("Folder name " + folder_name + " already exists. Supplying first conflicting folder information.")
			return ex.context_info['conflicts'][0]['id']
		else:
			raise


# Uploads file to given folder ID
# Returns dict with file ID and direct download URL
# If file already exists, returns information of existing file
def upload(dest_folder_id, file_name):
	to_upload = Path(upload_folder + "/" + file_name)
	dest_folder = client.folder(dest_folder_id).get()

	file_info = {'id':'', 'url':''}

	try:
		uploaded_file = dest_folder.upload(to_upload, file_name, preflight_check = True)

		direct_link = uploaded_file.get_shared_link_download_url()

		logger.info("Item " + file_name + " uploaded successfully.")
		return {'id':uploaded_file.object_id, 'url': direct_link}
	except BoxAPIException as ex:
		if ex.code == "item_name_in_use":
			logger.warning("Item name " + file_name + " already in use. Supplying first conflicting item information.")
			return {'id':ex.context_info['conflicts'][0]['id'], 'url':client.file(file_info['id']).get_shared_link_download_url()}
		else:
			raise


def delete_folder(id):
	return delete(client.folder(id).get())


def delete_file(id):
	try:
		result = delete(client.file(id).get())
	except BoxAPIException as ex:
		print(ex.message)
		if ex.code == "trashed":
			logger.warning("File ID " + id + " was already deleted and is in the trash.")
		elif ex.code == "not_found":
			logger.warning("File ID " + id + " was not found.")
		else:
			raise
	else:
		return result


def delete(item):
	result = item.delete()
	if result:
		logger.info("Item " + item.name + " deleted successfully.")
	else:
		logger.warning("There was a problem deleting item " + item.name)
	return result


def get_folder_contents(id):
	return client.folder(id).get_items(limit=100,offset=0)


def display_folder_contents(items):
	for item in items:
		print(item['name'])


if __name__ == '__main__':
	client = authenticate()

	create_folders()
	#display_folder_contents(get_folder_contents('0'))
