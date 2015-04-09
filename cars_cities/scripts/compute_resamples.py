import os
import sys
import us
import xlrd
import ftplib
import zipfile
import datetime

from os.path import join, exists

try:
    print 'Initializing ArcGIS python modules...'
    import arcpy
except ImportError:
    print 'Cannot import arcpy. Abort.'
    sys.exit(1)
else:
    arcpy.env.overwriteOutput = True
    print 'ArcGIS initialization complete'

from constants import LATLNGS_SHP_DIR, CITY_DIR, RESAMPLE_DIR, \
    CITY_BOUNDARY_SHP_DIR, PROJECTION_FILE, CITY_IDS
from utils import pickle_load

SEGMENT = 18
SEGMENT_SIZE = 10

CITY_IDS_CUSTOM = [115, 226, 129, 183, 203, 144, 197, 121, 132, 117, 229, 175,
                   192, 122, 196, 198, 268, 139, 234, 278, 146, 232, 161,
                   147, 195, 298]  # 289, 137,
CITY_IDS_CUSTOM = []

EXCLUDE = {117, 121, 137, 158, 289, 297}

ROADS_SHP_URL = 'ftp://ftp2.census.gov/geo/tiger/TIGER2014/ROADS/'
ROADS_TIGER_SHP = 'tl_2014_%s_roads'

# set up the fip codes lookup dictionary
fips_codes = xlrd.open_workbook(os.path.join(RESAMPLE_DIR, 'fips_codes.xls'))\
    .sheet_by_name('cqr_universe_fixedwidth_all')
fips_codes_dict = {}
for row in xrange(fips_codes.nrows):
    key = (fips_codes.cell_value(row, 5).lower(), fips_codes.cell_value(row, 1))
    fips_code = fips_codes.cell_value(row, 1) + fips_codes.cell_value(row, 2)
    if key not in fips_codes_dict:
        fips_codes_dict[key] = {fips_code}
    else:
        fips_codes_dict[key].add(fips_code)


def export_to_png(shp, output_dir):
    mxd = arcpy.mapping.MapDocument(join(output_dir, 'test.mxd'))
    df = arcpy.mapping.ListDataFrames(mxd, '*')[0]
    shp_layer = arcpy.mapping.Layer(shp)
    arcpy.mapping.AddLayer(df, shp_layer, 'BOTTOM')
    arcpy.RefreshActiveView()
    arcpy.RefreshTOC()


def log(msg, *args):
    print ('[%s] Segment %s: ' % (datetime.datetime.now().strftime('%H:%M:%S'), SEGMENT) + msg) % args


def fetch_road_shp(output_dir, fips_set):
    road_shps = set()
    for fips in fips_set:
        roads_shp = ROADS_TIGER_SHP % fips
        roads_shp_zip = roads_shp + '.zip'
        roads_shp_zip_path = join(output_dir, roads_shp_zip)
        roads_shp_path = join(output_dir, roads_shp + '.shp')
        roads_shp = roads_shp + '.zip'

        if not exists(roads_shp_zip_path):
            ftp = ftplib.FTP('ftp2.census.gov')
            ftp.login()
            ftp.cwd('geo/tiger/TIGER2014/ROADS/')
            log('No %s found. Downloading...', roads_shp_zip)
            try:
                ftp.retrbinary('RETR ' + roads_shp_zip, open(roads_shp_zip_path, 'wb+').write)
            except Exception as e:
                log('FAILED TO FETCH %s: %s', roads_shp_zip, str(e))
                continue
            log('Download complete for %s!', roads_shp_zip)
            ftp.close()

        # unzip the files if they haven't already
        if not exists(roads_shp_path):
            log('Unzipping %s...', roads_shp_zip)
            try:
                zfile = zipfile.ZipFile(roads_shp_zip_path)
            except Exception as e:
                log('CANNOT UNZIP! %s', str(e))
                continue
            for name in zfile.namelist():
                (_, filename) = os.path.split(name)
                log('Decompressing %s on %s', filename, output_dir)
                zfile.extract(name, output_dir)
            log('Unzip complete')

        road_shps.add(roads_shp_path)
    return road_shps


def compute_resampling(city_id):
    log('Computing resample points for %s', city_id)

    output_dir = join(RESAMPLE_DIR, str(city_id))
    if not exists(output_dir):
        os.makedirs(output_dir)
        log('Created %s', output_dir)
    else:
        log('%s already exists!', output_dir)

    # find the county fips codes
    city = pickle_load(join(CITY_DIR, str(city_id)))
    city_name = city['name'].strip().title()
    state_name = city['state'].strip().title()
    log('Looking up state info for %s...', state_name)

    if 'Utah' in state_name:
        state_name = 'UT'  # weird ass corner case..

    state = us.states.lookup(state_name)
    fips_set = fips_codes_dict[(city['name'].lower(), state.fips)]
    log('County fips codes for %s, %s: %s', city_name, state.name, fips_set)

    road_shps = fetch_road_shp(output_dir, fips_set)

    all_roads_shp = join(output_dir, 'all_roads.shp')
    if not exists(all_roads_shp):
        log('Merging %s into %s', list(road_shps), all_roads_shp)
        arcpy.Merge_management(list(road_shps), all_roads_shp)
        log('Merge complete')

    boundary_shp = join(CITY_BOUNDARY_SHP_DIR, 'tl_2014_%s_place.shp' % state.fips)
    city_boundary_shp = join(output_dir, 'city_boundary.shp')
    if not exists(city_boundary_shp):
        log('Fetching city boundary from %s...', boundary_shp)
        query = "\"NAME\" Like '%%%s%%'" % city['name'].title()
        log('Using query %s', query)
        arcpy.MakeFeatureLayer_management(boundary_shp, 'temp', query)
        arcpy.CopyFeatures_management('temp', city_boundary_shp)
        log('City boundary %s fetched', city_boundary_shp)

    all_roads_clipped_shp = join(output_dir, 'all_roads_clipped.shp')
    if not exists(all_roads_clipped_shp):
        log('Clipping all_roads into city boundary...')
        arcpy.Clip_analysis(all_roads_shp, city_boundary_shp, all_roads_clipped_shp)
        log('Clip complete')

    all_roads_buffered_shp = join(output_dir, 'all_roads_buffered.shp')
    if not exists(all_roads_buffered_shp):
        log('Buffering into %s...', all_roads_buffered_shp)
        arcpy.Buffer_analysis(all_roads_clipped_shp, all_roads_buffered_shp, '20 Meter')
        log('Buffering complete')

    sample_grid_shp = join(output_dir, 'sample_grid.shp')
    sample_grid_labels_shp = join(output_dir, 'sample_grid_label.shp')
    if not exists(sample_grid_shp):
        log('Creating fishnet...')
        desc = arcpy.Describe(all_roads_buffered_shp)
        arcpy.CreateFishnet_management(
            sample_grid_shp,
            str(desc.extent.lowerLeft),
            str(desc.extent.XMin) + ' ' + str(desc.extent.YMax + 10),
            '0.0003', '0.0003', '0', '0', str(desc.extent.upperRight),
            'LABELS',
            '#',
            'POLYLINE'
        )
        log('Fishnet creation complete')

    sample_grid_clipped_shp = join(output_dir, 'sample_grid_clipped.shp')
    if not exists(sample_grid_clipped_shp):
        log('Clipping fishnet to buffered roads...')
        arcpy.Clip_analysis(sample_grid_labels_shp, all_roads_buffered_shp,
                            sample_grid_clipped_shp)
        log('Clip fishnet to buffered roads complete')

    '''
    sample_grid_erased_shp = join(output_dir, 'sample_grid_erased.shp')
    if not exists(sample_grid_erased_shp):
        print 'Projecting using', PROJECTION_FILE
        # arcpy.DefineProjection_management(sample_grid_clipped_shp, PROJECTION_FILE)
        print 'Erasing existing samples from fishnet...'
        samples_shp = join(LATLNGS_SHP_DIR, str(city_id) + '.shp')
        arcpy.Erase_analysis(sample_grid_clipped_shp, samples_shp,
                            sample_grid_erased_shp, '20 Meter')
        print 'Erasing existing samples from fishnet complete'
    '''

    log('FINISHED computing resampling for %s: %s, %s', city_id, city_name, state.name)
    return sample_grid_clipped_shp
    log('======================END==========================')


if __name__ == '__main__':
    # shp = compute_resampling(196)
    # export_to_png(shp, join(RESAMPLE_DIR, str(196)))
    log('=====================BEGIN=========================')
    for city_id in CITY_IDS_CUSTOM or CITY_IDS[SEGMENT * SEGMENT_SIZE:(SEGMENT + 1) * SEGMENT_SIZE]:
        if city_id in EXCLUDE:
            continue
        compute_resampling(city_id)
