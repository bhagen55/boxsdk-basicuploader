import boxsdk
import json

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
print('user_login: ' + me['login'])

# Get root folder
root_folder = client.folder(folder_id='0').get()

# Create an assets folder
create_folder(root_folder, "Assets")
#root_folder.create_subfolder('Assets')

# Get items in root folder
items = root_folder.get_items(limit=100, offset=0)
print("Items in root:")
for item in items:
	print(item['name'])

# Get items in assets folder
assets_folder = root_folder.folder(folder_id='0').get()


def create_folder(base_folder, folder_name):
	try:
		base_folder.create_subfolder(folder_name)
	except boxsdk.exception.BoxAPIException:
		print("Error creating folder " + folder_name)
