// Load data tiles from an AJAX data source
L.TileLayer.Ajax = L.TileLayer.extend({
    _requests: [],
    _addTile: function (tilePoint) {
        var tile = { datum: null, processed: false };
        this._tiles[tilePoint.x + ':' + tilePoint.y] = tile;
        this._loadTile(tile, tilePoint);
    },
    // XMLHttpRequest handler; closure over the XHR object, the layer, and the tile
    _xhrHandler: function (req, layer, tile, tilePoint) {
        return function () {
            if (req.readyState !== 4) {
                return;
            }
            var s = req.status;
            if ((s >= 200 && s < 300) || s === 304) {
                tile.datum = JSON.parse(req.responseText);
                layer._tileLoaded(tile, tilePoint);
            } else {
                layer._tileLoaded(tile, tilePoint);
            }
            //layer = layer.bringToBack();
            //console.log('fuck');
        };
    },
    // Load the requested tile via AJAX
    _loadTile: function (tile, tilePoint) {
        this._adjustTilePoint(tilePoint);
        var layer = this;
        var req = new XMLHttpRequest();
        this._requests.push(req);
        req.onreadystatechange = this._xhrHandler(req, layer, tile, tilePoint);
        req.open('GET', this.getTileUrl(tilePoint), true);
        req.send();
    },
    _reset: function () {
        L.TileLayer.prototype._reset.apply(this, arguments);
        for (var i in this._requests) {
            this._requests[i].abort();
        }
        this._requests = [];
    },
    _update: function () {
        if (this._map && this._map._panTransition && this._map._panTransition._inProgress) { return; }
        if (this._tilesToLoad < 0) { this._tilesToLoad = 0; }
        L.TileLayer.prototype._update.apply(this, arguments);
    }
});


L.TileLayer.GeoJSON = L.TileLayer.Ajax.extend({
    // Store each GeometryCollection's layer by key, if options.unique function is present
    _keyLayers: {},

    // Used to calculate svg path string for clip path elements
    _clipPathRectangles: {},

    initialize: function (url, options, geojsonOptions) {
        L.TileLayer.Ajax.prototype.initialize.call(this, url, options);
        this.geojsonLayer = new L.GeoJSON(null, geojsonOptions);
        //console.log(this.geojsonLayer)
        //this.geojsonLayer.setZIndex(-1);
    },
    onAdd: function (map) {
        this._map = map;
        L.TileLayer.Ajax.prototype.onAdd.call(this, map);
        map.addLayer(this.geojsonLayer);
    },
    onRemove: function (map) {
        map.removeLayer(this.geojsonLayer);
        L.TileLayer.Ajax.prototype.onRemove.call(this, map);
    },
    _reset: function () {
        this.geojsonLayer.clearLayers();
        this._keyLayers = {};
        this._removeOldClipPaths();
        L.TileLayer.Ajax.prototype._reset.apply(this, arguments);
    },

    // Remove clip path elements from other earlier zoom levels
    _removeOldClipPaths: function  () {
        for (var clipPathId in this._clipPathRectangles) {
            var clipPathZXY = clipPathId.split('_').slice(1);
            var zoom = parseInt(clipPathZXY[0], 10);
            if (zoom !== this._map.getZoom()) {
                var rectangle = this._clipPathRectangles[clipPathId];
                this._map.removeLayer(rectangle);
                var clipPath = document.getElementById(clipPathId);
                if (clipPath !== null) {
                    clipPath.parentNode.removeChild(clipPath);
                }
                delete this._clipPathRectangles[clipPathId];
            }
        }
    },

    // Recurse LayerGroups and call func() on L.Path layer instances
    _recurseLayerUntilPath: function (func, layer) {
        if (layer instanceof L.Path) {
            func(layer);
        }
        else if (layer instanceof L.LayerGroup) {
            // Recurse each child layer
            layer.getLayers().forEach(this._recurseLayerUntilPath.bind(this, func), this);
        }
    },

    _clipLayerToTileBoundary: function (layer, tilePoint) {
        // Only perform SVG clipping if the browser is using SVG
        if (!L.Path.SVG) { return; }
        if (!this._map) { return; }

        if (!this._map._pathRoot) {
            this._map._pathRoot = L.Path.prototype._createElement('svg');
            this._map._panes.overlayPane.appendChild(this._map._pathRoot);
        }
        var svg = this._map._pathRoot;

        // create the defs container if it doesn't exist
        var defs = null;
        if (svg.getElementsByTagName('defs').length === 0) {
            defs = document.createElementNS(L.Path.SVG_NS, 'defs');
            svg.insertBefore(defs, svg.firstChild);
        }
        else {
            defs = svg.getElementsByTagName('defs')[0];
        }

        // Create the clipPath for the tile if it doesn't exist
        var clipPathId = 'tileClipPath_' + tilePoint.z + '_' + tilePoint.x + '_' + tilePoint.y;
        var clipPath = document.getElementById(clipPathId);
        if (clipPath === null) {
            clipPath = document.createElementNS(L.Path.SVG_NS, 'clipPath');
            clipPath.id = clipPathId;

            // Create a hidden L.Rectangle to represent the tile's area
            var tileSize = this.options.tileSize,
            nwPoint = tilePoint.multiplyBy(tileSize),
            sePoint = nwPoint.add([tileSize, tileSize]),
            nw = this._map.unproject(nwPoint),
            se = this._map.unproject(sePoint);
            this._clipPathRectangles[clipPathId] = new L.Rectangle(new L.LatLngBounds([nw, se]), {
                opacity: 0,
                fillOpacity: 0,
                clickable: false,
                noClip: true
            });
            this._map.addLayer(this._clipPathRectangles[clipPathId]);

            // Add a clip path element to the SVG defs element
            // With a path element that has the hidden rectangle's SVG path string  
            var path = document.createElementNS(L.Path.SVG_NS, 'path');
            var pathString = this._clipPathRectangles[clipPathId].getPathString();
            path.setAttribute('d', pathString);
            clipPath.appendChild(path);
            defs.appendChild(clipPath);
        }

        // Add the clip-path attribute to reference the id of the tile clipPath
        this._recurseLayerUntilPath(function (pathLayer) {
            pathLayer._container.setAttribute('clip-path', 'url(#' + clipPathId + ')');
        }, layer);
    },

    // Add a geojson object from a tile to the GeoJSON layer
    // * If the options.unique function is specified, merge geometries into GeometryCollections
    // grouped by the key returned by options.unique(feature) for each GeoJSON feature
    // * If options.clipTiles is set, and the browser is using SVG, perform SVG clipping on each
    // tile's GeometryCollection 
    addTileData: function (geojson, tilePoint) {
        var features = L.Util.isArray(geojson) ? geojson : geojson.features,
            i, len, feature;

        //console.log(i)

        if (features) {
            for (i = 0, len = features.length; i < len; i++) {
                // Only add this if geometry or geometries are set and not null
                feature = features[i];
                if (feature.geometries || feature.geometry || feature.features || feature.coordinates) {
                    this.addTileData(features[i], tilePoint);
                }
            }
            return this;
        }

        var options = this.geojsonLayer.options;

        if (options.filter && !options.filter(geojson)) { return; }

        var parentLayer = this.geojsonLayer;
        var incomingLayer = null;
        if (this.options.unique && typeof(this.options.unique) === 'function') {
            var key = this.options.unique(geojson);

            // When creating the layer for a unique key,
            // Force the geojson to be a geometry collection
            if (!(key in this._keyLayers && geojson.geometry.type !== 'GeometryCollection')) {
                geojson.geometry = {
                    type: 'GeometryCollection',
                    geometries: [geojson.geometry]
                };
            }

            // Transform the geojson into a new Layer
            try {
                incomingLayer = L.GeoJSON.geometryToLayer(geojson, options.pointToLayer, options.coordsToLatLng);

            }
            // Ignore GeoJSON objects that could not be parsed
            catch (e) {
                return this;
            }

            incomingLayer.feature = L.GeoJSON.asFeature(geojson);
            //incomingLayer.bringToBack();
            // Add the incoming Layer to existing key's GeometryCollection
            if (key in this._keyLayers) {
                parentLayer = this._keyLayers[key];
                parentLayer.feature.geometry.geometries.push(geojson.geometry);
            }
            // Convert the incoming GeoJSON feature into a new GeometryCollection layer
            else {
                this._keyLayers[key] = incomingLayer;
            }
        }
        // Add the incoming geojson feature to the L.GeoJSON Layer
        else {
            // Transform the geojson into a new layer
            try {
                incomingLayer = L.GeoJSON.geometryToLayer(geojson, options.pointToLayer, options.coordsToLatLng);
            }
            // Ignore GeoJSON objects that could not be parsed
            catch (e) {
                return this;
            }
            incomingLayer.feature = L.GeoJSON.asFeature(geojson);
        }
        incomingLayer.defaultOptions = incomingLayer.options;

        this.geojsonLayer.resetStyle(incomingLayer);

        if (options.onEachFeature) {
            options.onEachFeature(geojson, incomingLayer);
        }

        //#0354A5

        color_0 = "#dddddd";
        color_1 = "#0354A5";
        color_2 = "#037AC3";
        color_3 = "#03ADEF";
        color_4 = "#70D0F6";
        //#037AC3
        //#03ADEF
        //#70D0F6
        if (geojson.id == "state:01" ){
            incomingLayer.setStyle({fillColor: color_3})
        }
       // if (geojson.id == "state:02" ){
       //     incomingLayer.setStyle({fillColor: '#DDDDDD'})
       // }
        if (geojson.id == "state:04" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }
        if (geojson.id == "state:02" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_0})
        }


        if (geojson.id == "state:05" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:06" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }
        
        if (geojson.id == "state:08" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:09" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:10" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        //if (geojson.id == "state:11" ){
        //    console.log('sdf')
        //    incomingLayer.setStyle({fillColor: color_0})
        //}

       if (geojson.id == "state:12" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:13" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }

        if (geojson.id == "state:16" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:17" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:18" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:19" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:20" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:21" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }


        if (geojson.id == "state:22" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }

        if (geojson.id == "state:23" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:24" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }


        if (geojson.id == "state:25" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:26" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }


        if (geojson.id == "state:27" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:28" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:29" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:30" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }

        if (geojson.id == "state:31" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }

        if (geojson.id == "state:32" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:33" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }

        if (geojson.id == "state:34" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:35" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:36" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:37" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:38" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:39" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:40" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }

        if (geojson.id == "state:41" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:42" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }

        if (geojson.id == "state:44" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:45" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:46" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:47" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:48" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:49" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }

        if (geojson.id == "state:50" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:51" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_2})
        }

        if (geojson.id == "state:53" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }

        if (geojson.id == "state:54" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_1})
        }

        if (geojson.id == "state:55" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_4})
        }

        if (geojson.id == "state:56" ){
            //console.log('sdf')
            incomingLayer.setStyle({fillColor: color_3})
        }



        parentLayer.addLayer(incomingLayer);
        parentLayer.bringToBack();
        
        // If options.clipTiles is set and the browser is using SVG
        // then clip the layer using SVG clipping
        if (this.options.clipTiles) {
            this._clipLayerToTileBoundary(incomingLayer, tilePoint);
        }
        return this;
    },

    _tileLoaded: function (tile, tilePoint) {
        L.TileLayer.Ajax.prototype._tileLoaded.apply(this, arguments);
        if (tile.datum === null) { return null; }
        this.addTileData(tile.datum, tilePoint);
    }
});