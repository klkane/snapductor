import yaml
import json
import requests

class SnapductorUser:
    username = None
    is_authenticated = True
    is_active = True
    is_anonymous = False

    def get_id( self ):
        return self.username

    def __init__( self, username ):
        self.username = username

class SnapLogic:
    config = None
    test_assets = None
    prod_assets = None
    test_projects = None
    prod_projects = None

    def __init__( self ):
        with open( 'config.yml' ) as f:
            self.config = yaml.load( f, Loader=yaml.FullLoader )
        self.load_assets()

    def comparePaths( self, path1, path2 ):
        path1 = path1.replace( self.config['test_target'], '' )
        path1 = path1.replace( self.config['prod_target'], '' )
        path2 = path2.replace( self.config['test_target'], '' )
        path2 = path2.replace( self.config['prod_target'], '' )
        return path1 == path2


    def reverseAssetExists( self, asset_path, asset_type ):
        prod_asset_path = asset_path
        test_asset_path = asset_path.replace( self.config['prod_target'], self.config['test_target'] )
        
        prod_asset = None
        test_asset = None
        
        if asset_type == 'project':
            for asset in self.test_projects:
                if asset['path'] == test_asset_path:
                    test_asset = asset

            for asset in self.prod_projects:
                if asset['path'] == prod_asset_path:
                    prod_asset = asset

        elif asset_type == 'pipeline':
            for asset in self.test_projects:
                for inner_asset in asset['pipelines']:
                    if inner_asset['path'] == test_asset_path:
                        test_asset = inner_asset
            for asset in self.prod_projects:
                for inner_asset in asset['pipelines']:
                    if inner_asset['path'] == prod_asset_path:
                        prod_asset = inner_asset
            
        elif asset_type == 'task':
            for asset in self.test_projects:
                for inner_asset in asset['tasks']:
                    if inner_asset['path'] == test_asset_path:
                        test_asset = inner_asset
            for asset in self.prod_projects:
                for inner_asset in asset['tasks']:
                    if inner_asset['path'] == prod_asset_path:
                        prod_asset = inner_asset
        
        if test_asset is None:
            return False

        return True

    def getStatus( self, asset_path, asset_type ):
        test_asset_path = asset_path
        prod_asset_path = asset_path.replace( self.config['test_target'], self.config['prod_target'] )

        prod_asset = None
        test_asset = None
        if asset_type == 'project':
            for asset in self.test_projects:
                if asset['path'] == test_asset_path:
                    test_asset = asset

            for asset in self.prod_projects:
                if asset['path'] == prod_asset_path:
                    prod_asset = asset

        elif asset_type == 'pipeline':
            for asset in self.test_projects:
                for inner_asset in asset['pipelines']:
                    if inner_asset['path'] == test_asset_path:
                        test_asset = inner_asset
            for asset in self.prod_projects:
                for inner_asset in asset['pipelines']:
                    if inner_asset['path'] == prod_asset_path:
                        prod_asset = inner_asset
            
        elif asset_type == 'task':
            for asset in self.test_projects:
                for inner_asset in asset['tasks']:
                    if inner_asset['path'] == test_asset_path:
                        test_asset = inner_asset
            for asset in self.prod_projects:
                for inner_asset in asset['tasks']:
                    if inner_asset['path'] == prod_asset_path:
                        prod_asset = inner_asset

        if prod_asset is None:
            return "NEW"

        if test_asset is None:
            return "UNKNOWN"

        time_field = 'time_updated'

        if asset_type == 'pipeline':
            time_field = 'update_time'
    
        if prod_asset[time_field] < test_asset[time_field]:
            return "MODIFIED"

        return ""

    def delete_asset( self, asset_type, asset_path ):
        headers = {"Authorization": "Bearer " + self.config['delete_asset_api_bearer']}
        params = { "asset_type": asset_type, "asset_path": asset_path }
        result = requests.get(self.config['delete_asset_api_url'], params=params, headers=headers)

    def migrate_asset( self, asset_type, migrate_from, migrate_to ):
        headers = {"Authorization": "Bearer " + self.config['migrate_asset_api_bearer']}
        params = { "asset_type": asset_type, "migrate_from": migrate_from, "migrate_to": migrate_to }
        result = requests.get(self.config['migrate_asset_api_url'], params=params, headers=headers)

    def refresh_assets( self ):
        headers = {"Authorization": "Bearer " + self.config['list_assets_api_bearer']}
        params = {"asset_path": self.config['test_target'] }
        result = requests.get(self.config['list_assets_api_url'], params=params, headers=headers)
        self.test_assets = json.loads( result.text )
        f = open( 'test_assets.json', "w" )
        f.write( result.text )
        f.close()
        params = {"asset_path": self.config['prod_target'] }
        result = requests.get(self.config['list_assets_api_url'], params=params, headers=headers)
        self.test_assets = json.loads( result.text )
        f = open( 'prod_assets.json', "w" )
        f.write( result.text )
        f.close()
        self.load_assets()

    def getProjects( self, environment = 'test' ):
        projects = []
        assets = None
        i = 0

        if environment == 'test':
            assets = self.test_assets
        elif environment == 'prod':
            assets = self.prod_assets
        else:
            return []
    
        for asset in assets:
            if 'project' in asset:
                projects.append( asset['project'] )
            
                projects[i]['pipelines'] = []
                projects[i]['tasks'] = []
                for inner_asset in assets:
                    if 'pipeline' in inner_asset:
                        if inner_asset['pipeline']['path_id'] == projects[i]['path']:
                            projects[i]['pipelines'].append( inner_asset['pipeline'] )
                    if 'task' in inner_asset:
                        # task path doesn't have a leading / but other assets do, i used an or clause here 
                        # in case snap logic ever changes this behavior
                        if inner_asset['task']['path_id'] == projects[i]['path'] or inner_asset['task']['path_id'] == projects[i]['path'][1:]:
                            inner_asset['task']['path'] = inner_asset['task']['original']['path']
                            inner_asset['task']['time_updated'] = inner_asset['task']['original']['time_updated']
                            projects[i]['tasks'].append( inner_asset['task'] )
                i = i + 1
            
        return projects

    def load_assets( self ):
        try:
            with open( 'test_assets.json' ) as f:
                self.test_assets = json.load( f )
            with open( 'prod_assets.json' ) as f:
                self.prod_assets = json.load( f )
        except FileNotFoundError:
            self.refresh_assets()

        self.test_projects = self.getProjects()
        self.prod_projects = self.getProjects( environment = 'prod' )
        
