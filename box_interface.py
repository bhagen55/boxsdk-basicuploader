import boxsdk
from boxsdk.exception import BoxAPIException
import json
import os, errno
from pathlib import Path
import logging

# Logging setup
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# global client variable gets set at authentication
# needed by basically all functions
client = None


def authenticate(appauth_file_path):
	"""
	Get authorization info and authenticate
	Private key is pulled from the .json file provided
	by box and saved to ./keys/privkey

	:param appauth_file_path:
		file path, including full filename, to box .json authentication file
	:returns:
		authenticated box client object that can make calls to the box API
	"""

	appauth_file = Path(appauth_file_path)

	# Open provided appauth file
	# TODO: Error checking here for filesystem errors
	with open(appauth_file) as f:
		auth_info = json.load(f)

	# Pull private key info from appauth file and save it as
	# 'privkey' as the JWTAuth object wants it as a seperate file
	#
	# The file gets named by taking the name of the appauth file and adding
	# "_privkey" to the end of it. So an appauth file named "boxauth.json"
	# would generate a "boxauth_privkey" file.
	# TODO: Error checking here for filesystem errors
	with open(appauth_file.parent + "/" + appauth_file.stem + "_privkey" ,'w') as f:
		f.write(auth_info["boxAppSettings"]["appAuth"]["privateKey"])

	# Authentication info
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
	boxclient = boxsdk.Client(auth)

	# Get user info
	me = boxclient.user(user_id='me').get()
	logger.info('User Login: ' + me['login'])

	return boxclient


def upload(dest_folder, file_path):
	"""
	Uploads a file to a destination folder

	:param dest_folder:
		folder object to upload file into
	:param file_path:
		pathlib object of file to upload
	:returns:
		uploaded file object or none if already in use
	"""
	try:
		uploaded_file = dest_folder.upload(file_path.parent, file_path.name, preflight_check = True)

		logger.info("Item " + file_path.name + " uploaded successfully.")
		return uploaded_file
	except BoxAPIException as ex:
		if ex.code == "item_name_in_use":
			logger.warning("Item name " + file_path.name + " already in use.")
			return None
		else:
			raise


### Folder Operations ###

def get_folder_contents(folder, limit):
	"""
	Gets contents of a folder (nested folders and files)
	Can provide a limit of how many results to return

	:param folder:
		folder object to get contents of
	:param limit:
		integer limit of how many results to return
	"""
	return(folder.get_items(limit, offset=0))


def create_folder(base_folder, new_folder_name):
	"""
	Creates a folder within a given folder
	If folder already exists, returns the first conflicting folder's info

	:param base_folder:
		folder object to make new folder inside of
	:param new_folder_name:
		string to name new folder
	:returns:
		folder object of new folder or conflicting folder object
	"""
	try:
		new_folder = base_folder.create_subfolder(new_folder_name)
		logger.info("Folder " + new_folder_name + " created successfully.")
		return new_folder
	except BoxAPIException as ex:
		if ex.code == "item_name_in_use":
			logger.warning("Folder name " + folder_name + " already exists. Supplying first conflicting folder information.")
			return client.folder(ex.context_info['conflicts'][0]['id']).get() # TODO: Test this
		else:
			raise


def delete_folder(id, force):
	result = client.folder(id).delete(recursive=force)

	if result:
		logger.info("Item deleted successfully.")
	else:
		logger.warning("There was a problem deleting item")
	return result


def get_folder(id):
	return client.folder(id).get()


def rename_folder(id, new_name):
	client.folder(id).rename(new_name)


### File Operations ###

def get_direct_download(file):
	"""
	Get a direct permalink to file with open access and no expiration

	:param file: file object to upload
	:returns: string of direct url download
	"""
	return file.get_shared_link_download_url(access="open", unshared_at=None)


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


def delete_file(id):
	result = client.file(id).delete()

	if result:
		logger.info("Item deleted successfully.")
	else:
		logger.warning("There was a problem deleting item")
	return result


def get_file(id):
	return client.file(id).get()


def rename_file(id, new_name):
	client.file(id).rename(new_name)
