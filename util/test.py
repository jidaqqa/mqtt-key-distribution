from util.yaml_config_rw import YmalReader

# cl_list = {}
yml = YmalReader()
cl_list = yml.read_yaml("clients_with_keys.yml")

if cl_list is not None:
    print("In")
    if bool(cl_list.get("Ji")):
        print("Checking in")
    else:
        print("Vlaue not In")
else:
    print("Else")