import yaml
import json
import requests

class SnapLogic:
    config = None
    test_assets = None
    prod_assets = None

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

    def getStatus( self, asset_path ):
        asset = None
        for ta in self.prod_assets:
            if self.comparePaths( ta['path'], asset_path ):
                asset = ta

        if asset is None:
            return "NEW"

        test_asset = None
        for ta in self.test_assets:
            if self.comparePaths( ta['path'], asset_path ):
                test_asset = ta

        if test_asset is None:
            return "UNKOWN"

        if test_asset['update_time'] > asset['update_time']:
            return "MODIFIED"
        
        return ""

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

    def load_assets( self ):
        try:
            with open( 'test_assets.json' ) as f:
                self.test_assets = json.load( f )
            with open( 'prod_assets.json' ) as f:
                self.prod_assets = json.load( f )
        except FileNotFoundError:
            self.refresh_assets()
        
