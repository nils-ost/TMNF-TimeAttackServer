import xml.etree.ElementTree as ET

tree = ET.parse('dedicated_cfg.txt')

tree.find('server_options').find('name').text = 'Test'
tree.find('server_options').find('ladder_mode').text = 'inactive'
tree.find('system_config').find('xmlrpc_allowremote').text = 'True'

tree.write('dedicated_cfg_new.txt', encoding='utf-8', xml_declaration=True, short_empty_elements=False)
