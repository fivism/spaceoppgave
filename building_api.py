import json
import sys
import time             # timestamping for concurrent-use resolution
import geopandas as gpd
from shapely.geometry import Polygon

DEBUG_VERBOSE = False

class HeightsLimitsProc:
    """ This class processes geopolygons described in
        an input GeoJSON file (sample.json), catches errors
        and has the ability to output diced-up-polygons comprised
        the two overlaid (gpd intersect op)
    """

    def __init__(self, limits_in, heights_in):
        """ Class has list objects of all geopolygons, one for
            building limit extent(s), one for heightplateaus,
            one for union
        """
        # Filenames for later recomposition/use
        self.limits_file = limits_in
        self.heights_file = heights_in

        # Read in limits to a reference stub
        with open(self.limits_file, 'r') as f:
            loaded_limits = json.load(f)
        self.limits = loaded_limits['building_limits']['features']

        # Read in heights to a reference stub
        with open(self.heights_file, 'r') as f:
            loaded_heights = json.load(f)
        self.heights = loaded_heights['height_plateaus']['features']

        # Current hybrid features
        self.hybrid_features = None             # Unionize fills this

        ####
        # Class feature for possible conflict resolution
        # and document history:
        # Simplistic linear history of valid featuresets receives new appends
        # on every good validate() call. Saves timestamp, current limits,
        # current plateaus and current hybrid features.
        self.good_validation_history = []

        if DEBUG_VERBOSE:
            print("LIMITS FEATURES:")
            print(loaded_limits['building_limits']['features'])
            print("\nHEIGHTS FEATURES:")
            print(loaded_heights['height_plateaus']['features'])
            print('\n__init__: lims_file: {} | heights_json: {}'.format(
                    self.limits_file, self.heights_file))
            print('Limits features loaded: {}'.format(len(self.limits)))
            print('Heights features loaded: {}'.format(len(self.heights)))

    def update_heights(self, heights_in):
        """ Tries to read in new heights from a file
            Returns boolean result of validate() to give feedback on
            model integrity after update (and save new changes if good)
        """
        with open(heights_in, 'r') as f:
            loaded_heights = json.load(f)
        self.heights = loaded_heights['height_plateaus']['features']
        return self.validate()

    def update_limits(self, limits_in):
        """ Tries to read in new limits from a file
            Returns boolean result of validate() to give feedback on
            model integrity after update (and save new changes if good)
        """
        with open(limits_in, 'r') as f:
            loaded_limits = json.load(f)
        self.limits = loaded_limits['building_limits']['features']
        return self.validate()

    def unionize(self):
        """ Calls shapely.ops to generate unionized polygons
            with everything inside the building_limits now
        """
        ## Rip out limits coords
        coords = [cpair for cpair in self.limits[0]['geometry']['coordinates'][0]]
        lim_poly_gs = gpd.GeoSeries(Polygon(coords))

        self.hybrid_features = []   # ready hybrid_features

        # This way assumes 1 building limit polygon * N height plateaus
        for feature in self.heights:
            height_coords = [cpair for cpair in feature['geometry']['coordinates'][0]]
            hei_poly_gs = gpd.GeoSeries(Polygon(height_coords))
            inter = lim_poly_gs.intersection(hei_poly_gs)       # lean on geoseries to give us intersect polygon
            inter_json = json.loads(inter.to_json())            # output that json from the new obj
            inter_json['features'][0]['properties'] = feature['properties'] # tag on applicable elevation
            inter_json['features'][0].pop('id', None)       # pop off cruft (this is ugly)
            inter_json['features'][0].pop('bbox', None)     # no need for bbox here
            self.hybrid_features.append(inter_json['features'][0])


    def validate(self):
        """ Validates that extent of building limits lies within
            height plateau extents AND that no gaps exist inself.
            Right now can only be called if a hybrid feature set has been made.
        """
        def valid_areas():
            """ One parity check is to sum the area of the hybrid features
                and compare to original limit's total area
            """
            coords = [cpair for cpair in self.limits[0]['geometry']['coordinates'][0]]
            lim_poly_gs = gpd.GeoSeries(Polygon(coords))
            sum = 0
            for feature in self.hybrid_features:
                height_coords = [cpair for cpair in\
                                    feature['geometry']['coordinates'][0]]
                hei_poly_gs = gpd.GeoSeries(Polygon(height_coords))
                sum += hei_poly_gs.area.tolist()[0]         # convert back to float64 from pandas Series

            tol = 1E-15         # No idea what this *should* be at this scale
                                # Border for false failure on provided data is around 1E-18

            return abs(lim_poly_gs.area.tolist()[0] - sum) < tol

        def valid_integrity():
            """ #TODO Another kind of integrity test could go here
            """
            return True

        if self.hybrid_features != None:
            valid = valid_areas() and valid_integrity()
            if valid:   # toss onto the good validation history with a timestamp
                self.good_validation_history.append([time.time(), \
                                                    self.limits,
                                                    self.heights,
                                                    self.hybrid_features])
            return valid

        else:
            print("Hybrid features not generated yet. No validation check run")
            return False

    def write_out(self, filename):
        """ Writes out the mixed intersection features from last known good
            feature set from good_validation_history
        """
        if self.good_validation_history:
            newest_good_hybrids = self.good_validation_history[-1][-1]
            out_dict = {'hybrid_features': [{'type': 'FeatureCollection'},\
                {'features': newest_good_hybrids}]}
            with open(filename, 'w') as outfile:
                json.dump(out_dict, outfile, sort_keys=True, indent=2)
            print("Written to {}".format(filename))
        else:
            print("Error: Currently no generated features to be written")

if __name__ == '__main__':
    """ Demo assumes we have files 'limits.json' and 'heights.json' in
        the same directory. Outputs new features json data to 'out.json'
    """
    print("Testing HeightsLimitsProc:")
    try:
        tmp_class = HeightsLimitsProc('limits.json', 'heights.json')

        # Generate hybrid intersection features with elevation properties applied
        tmp_class.unionize()
        print("\nHybridized features generated.")

        # Run available validation tests on current, generated features
        if tmp_class.validate():
            print("Validation passed!")
            # Write out indented, formatted json of these new features
            tmp_class.write_out('out.json')
        else:
            print("Validation failed!")

    except FileNotFoundError:
        print("Either limits.json or heights.json not in directory")
        sys.exit(1)
    else:
        sys.exit(1)
