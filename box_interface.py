import boxsdk
from boxsdk.exception import BoxAPIException
import json
import os, errno
from pathlib import Path
import logging

# Logging setup
logging.basicConfig(level=logging.WARNING)


class box_interface:
	def __init__(self, appauth_file_path):
		self.logger = logging.getLogger(__name__)

		self.client = self.authenticate(appauth_file_path)

	def authenticate(self, appauth_file_path):
		"""
		Get authorization info and authenticate
		Private key is pulled from the .json file provided
		by box and saved to ./keys/privkey

		:param appauth_file_path: file path, including full filename, to box .json authentication file
		:returns: authenticated box client object that can make calls to the box API
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
		with open(str(appauth_file.parent) + "/" + str(appauth_file.stem) + "_privkey" ,'w') as f:
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
		self.logger.info('User Login: ' + me['login'])

		return boxclient


	def upload(self, dest_folder, file_path):
		"""
		Uploads a file to a destination folder

		:param dest_folder: folder object to upload file into
		:param file_path: pathlib object of file to upload
		:returns: uploaded file object or none if already in use
		"""
		try:
			uploaded_file = dest_folder.upload(file_path, file_path.name, preflight_check = True)

			self.logger.info("Item " + file_path.name + " uploaded successfully.")
			return uploaded_file
		except BoxAPIException as ex:
			if ex.code == "item_name_in_use":
				self.logger.warning("Item name " + file_path.name + " already in use.")
				return None
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
			self.logger.info("Folder " + new_folder_name + " created successfully.")
			return new_folder
		except BoxAPIException as ex:
			if ex.code == "item_name_in_use":
				logger.warning("Folder name " + folder_name + " already exists. Supplying first conflicting folder information.")
				return client.folder(ex.context_info['conflicts'][0]['id']).get() # TODO: Test this
			else:
				raise


	# TODO: Error checking of deleting a folder that doesn't exist or is trashed
	def delete_folder(self, folder, force=False):
		"""
		Deletes a folder

		:param folder: folder object to be deleted
		:param force: boolean to force deletion even if folder is not empty
		"""
		try:
			result = folder.delete(recursive=force)
			self.logger.info("Item deleted successfully.")
			return result
		except BoxAPIException as ex:
			if ex.code == "folder_not_empty":
				self.logger.warning("Folder not deleted: not empty and force not chosen.")
				return False
			else:
				raise
				

	# TODO: error checking of getting an ID that doesnt exist
	def get_folder(self, id):
		"""
		Gets the folder object attached to an ID number

		:param id: ID number of desired folder
		:returns: folder object
		"""
		return self.client.folder(id).get()


	# TODO: error checking of changing to name that already exists, etc
	def rename_folder(self, folder, new_name):
		"""
		Renames a folder

		:param folder: folder object to be renamed
		:param new_name: string name to give to folder
		"""
		folder.rename(new_name)


	### File Operations ###

	def get_direct_download(self, file):
		"""
		Get a direct permalink to file with open access and no expiration

		:param file: file object to upload
		:returns: string of direct url download
		"""
		return file.get_shared_link_download_url(access="open", unshared_at=None)


	# TODO: What does this return???
	def delete_file(self, file):
		"""
		Deletes a file

		:param file: file object to be deleted
		:returns: unknown
		"""
		try:
			result = file.delete()
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


	# TODO: Error checking of renaming to something that already exists, illegal characters
	def rename_file(self, file, new_name):
		"""
		Renames a file

		:param file: file object to be renamed
		:param new_name: string name to give file
		"""
		file.rename(new_name)


	def get_file(self, id):
		"""
		Gets the file object attached to an ID number

		:param id: ID number of desired file
		:returns: file object
		"""
		return self.client.file(id).get()
