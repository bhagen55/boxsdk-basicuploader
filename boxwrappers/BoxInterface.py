import boxsdk
from boxsdk.exception import BoxAPIException
import json
import os, errno
from pathlib import Path
import logging

# Logging setup



class BoxInterface:
	def __init__(self, appauth_file_path):
		self.client = self.authenticate(appauth_file_path)

	def authenticate(self, appauth_file_path):
		"""
		Get authorization info and authenticate
		Private key is pulled from the .json file provided
		by box and saved to ./keys/privkey

		:param appauth_file_path: file path, including full filename, to box .json authentication file
		:returns: authenticated box client object that can make calls to the box API
		"""
		auth_info, privkey_path = self.extractAuthInfo(Path(appauth_file_path))

		# Authentication info
		auth = boxsdk.JWTAuth(
			client_id=auth_info["boxAppSettings"]["clientID"],
			client_secret=auth_info["boxAppSettings"]["clientSecret"],
			enterprise_id=auth_info["enterpriseID"],
			jwt_key_id=auth_info["boxAppSettings"]["appAuth"]["publicKeyID"],
			rsa_private_key_file_sys_path=privkey_path,
			rsa_private_key_passphrase=auth_info['boxAppSettings']['appAuth']['passphrase'].encode("ascii")
		)

		# Authenticate
		access_token = auth.authenticate_instance()
		boxclient = boxsdk.Client(auth)

		# Get user info
		me = boxclient.user(user_id='me').get()
		logging.info('User Login: ' + me['login'])

		return boxclient


	def extractAuthInfo(self, appauth_file_path):
		"""
		Pull auth info and private key from appauth file.

		The privkey file gets named by taking the name of the appauth file and adding
		"_privkey" to the end of it. So an appauth file named "boxauth.json"
		would generate a "boxauth_privkey" file.

		Assumes: File at appauth_file_path exists

		:param appauth_file_path: Path object pointing to appauth file
		:returns: tuple of information from authfile and path to generated privkey
		"""
		with open(appauth_file_path) as f:
			auth_info = json.load(f)

		privkey_save_path = str(appauth_file_path.parent) + "/" + str(appauth_file_path.stem) + "_privkey"
		with open(privkey_save_path ,'w') as f:
			f.write(auth_info["boxAppSettings"]["appAuth"]["privateKey"])

		return auth_info, privkey_save_path


	def upload(self, dest_folder, file_path):
		"""
		Uploads a file to a destination folder

		:param dest_folder: folder object to upload file into
		:param file_path: pathlib object of file to upload
		:returns: uploaded file object or none if already in use
		"""
		try:
			uploaded_file = dest_folder.upload(file_path, file_path.name, preflight_check = True)

			logging.info("Item " + file_path.name + " uploaded successfully.")
			return uploaded_file
		except BoxAPIException as ex:
			if ex.code == "item_name_in_use":
				logging.warning("Item name " + file_path.name + " already in use.")
				return None
			else:
				raise


	def rename(self, item, new_name):
		"""
		Renames an item

		:param item: item object to be renamed
		:param new_name: string name to give item
		"""
		try:
			item.rename(new_name)
			return True
		except BoxAPIException as ex:
			if ex.code == "item_name_in_use":
				logging.warning("Item name " + new_name + " already in use.")
				return False
			else:
				raise


	### Folder Operations ###

	def get_folder_contents(self, folder, limit=100):
		"""
		Gets contents of a folder (nested folders and files)
		Can provide a limit of how many results to return

		:param folder: folder object to get contents of
		:param limit: integer limit of how many results to return
		"""
		return(folder.get_items(limit, offset=0))


	def create_folder(self, base_folder, new_folder_name):
		"""
		Creates a folder within a given folder
		If folder already exists, returns the first conflicting folder's info

		:param base_folder: folder object to make new folder inside of
		:param new_folder_name: string to name new folder
		:returns: folder object of new folder or conflicting folder object
		"""
		try:
			new_folder = base_folder.create_subfolder(new_folder_name)
			logging.info("Folder " + new_folder_name + " created successfully.")
			return new_folder
		except BoxAPIException as ex:
			if ex.code == "item_name_in_use":
				logger.warning("Folder name " + folder_name + " already exists. Supplying first conflicting folder information.")
				return client.folder(ex.context_info['conflicts'][0]['id']).get() # TODO: Test this
			else:
				raise


	def delete_folder(self, folder, force=False):
		"""
		Deletes a folder

		:param folder: folder object to be deleted
		:param force: boolean to force deletion even if folder is not empty
		"""
		try:
			result = folder.delete(recursive=force)
			logging.info("Item deleted successfully.")
			return result
		except BoxAPIException as ex:
			if ex.code == "folder_not_empty":
				logging.warning("Folder not deleted: not empty and force not chosen.")
				return False
			if ex.code == "access_denied_insufficient_permissions":
				logging.warning("Access Denied. Most likely tried to modify root.")
			else:
				raise


	def get_folder(self, id):
		"""
		Gets the folder object attached to an ID number

		:param id: ID number of desired folder
		:returns: folder object
		"""
		return self.client.folder(id).get()


	### File Operations ###

	def get_direct_download(self, file):
		"""
		Get a direct permalink to file with open access and no expiration

		:param file: file object to upload
		:returns: string of direct url download
		"""
		return file.get_shared_link_download_url(access="open", unshared_at=None)


	def delete_file(self, file):
		"""
		Deletes a file

		:param file: file object to be deleted
		"""
		try:
			file.delete()
		except BoxAPIException as ex:
			if ex.code == "trashed":
				logger.warning("File ID " + id + " was already deleted and is in the trash.")
			elif ex.code == "not_found":
				logger.warning("File ID " + id + " was not found.")
			else:
				raise


	def get_file(self, id):
		"""
		Gets the file object attached to an ID number

		:param id: ID number of desired file
		:returns: file object
		"""
		return self.client.file(id).get()
