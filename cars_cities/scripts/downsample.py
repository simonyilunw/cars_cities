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

from constants import LATLNGS_SHP_DIR, DOWNSAMPLE_DIR, PROJECTION_FILE, CITY_IDS


SEGMENT = 'all'
CITY_IDS_CUSTOM = []


def log(msg, *args):
    print ('[%s] Segment %s: ' % (datetime.datetime.now().strftime('%H:%M:%S'), SEGMENT) + msg) % args


def downsample(city_id):
    log('Downsampling points for %s', city_id)

    output_dir = join(DOWNSAMPLE_DIR, str(city_id))
    if not exists(output_dir):
        os.makedirs(output_dir)
        log('Created %s', output_dir)
    else:
        log('%s already exists!', output_dir)

    samples_shp = join(LATLNGS_SHP_DIR, '%s.shp' % city_id)

    downsampling_fishnet_poly_shp = join(output_dir, 'downsampling_fishnet.shp')
    downsampling_fishnet_label_shp = join(output_dir, 'downsampling_fishnet_label.shp')

    if not exists(downsampling_fishnet_poly_shp):
        log('Creating fishnet...')
        desc = arcpy.Describe(samples_shp)
        arcpy.CreateFishnet_management(
            downsampling_fishnet_poly_shp,
            str(desc.extent.lowerLeft),
            str(desc.extent.XMin) + ' ' + str(desc.extent.YMax + 10),
            '0.0012', '0.0012', '0', '0', str(desc.extent.upperRight),
            'LABELS',
            '#',
            'POLYGON'
        )
        log('Fishnet creation complete')

    samples_identity_shp = join(output_dir, 'samples_identity.shp')
    if not exists(samples_identity_shp):
        log('Computing identity...')
        arcpy.Identity_analysis(samples_shp, downsampling_fishnet_poly_shp, samples_identity_shp)
        log('Identity complete')

    samples_stats = join(output_dir, 'samples_stats')
    if not exists(join(output_dir, 'info')):
        log('Starting summary statistics...')
        arcpy.Statistics_analysis(samples_identity_shp, samples_stats, [['price', 'MEAN']], 'FID_downsa')
        log('Summary statistics complete')

    log('Detecting if join has already been done...')
    join_done = False
    fields = arcpy.ListFields(downsampling_fishnet_label_shp)
    for field in fields:
        if field.name == 'MEAN_PRICE': join_done = True

    if not join_done:
        log('Performing table join on FID:FID_DOWNSA...')
        arcpy.JoinField_management(downsampling_fishnet_label_shp, 'FID', samples_stats, 'FID_DOWNSA', ['MEAN_PRICE'])
        log('Table join on FID:FID_DOWNSA done.')

    log('Defining projection...')
    arcpy.DefineProjection_management(downsampling_fishnet_label_shp, PROJECTION_FILE)

    log('FINISHED downsampling %s', city_id)
    return downsampling_fishnet_label_shp
    log('======================END==========================')


if __name__ == '__main__':
    # shp = compute_resampling(196)
    # export_to_png(shp, join(RESAMPLE_DIR, str(196)))
    log('=====================BEGIN=========================')
    for city_id in CITY_IDS_CUSTOM or CITY_IDS:
        downsample(city_id)
