    var geocoder;
    var gMEvent					=undefined;
    
	var Polyline				=undefined;	
	var Polygon					=undefined;	
	var lineas					=new Array();
	var linea;
	
	var localizacion;		
	var elocation;		

	var localizaciones			=new Array();
	var localizacion_anterior;
	var vehicle_data			=new Array();
	var locationsMarker 		=new Array();
	var infoGeofences 			=new Array();
	var showGeofences 			=0;
	var device_active			=0;
	var device_random			=0;
	var coordinate_active		=undefined;
	var simulation_action		="stop";
	var simulation_time			=100;
	var simulation_stop			=0;
	var waypts					=new Array();
	var devices_all				=new Array();
	var labels					=new Array();		

	var ida						=new Array();
	var vuelta					=new Array();
	var points_route			="";
	
	var isimulacion				=1;
	var row_index			    =undefined;
	var row						={};
    var local                   ={};
    var gpsmaps_obj;
    var streetonline_obj;
    var maponline_obj;
    var map;
    var class_gpsmap;
    var actualizaciones         =0;
        
odoo.define('gpsmap', function(require){
    "use strict";
    var core                    = require('web.core');
    var Widget                  = require('web.Widget');
    var rpc                     = require('web.rpc');

    map                         =undefined;    
    local.vehicles              =Array();
    local.geofences             =Array();
    local.positions             =undefined;    
    local.gpsmap                =undefined;
    local.actualizaciones       =0;        
    
    //////////////////////////////////////////////////////////////
    ////////  CLASS GPSMAP  
    //////////////////////////////////////////////////////////////
    class_gpsmap = Widget.extend({
        //////////////////////////////////////////////////////////////
        geofences_paint: function() 
        {
            setTimeout(function()
            {       
                console.log("Pinta las geocercas");
                var igeofences;
                var geofences   =local.geofences;
                for(igeofences in geofences)
                {		                
                    var geofence                    =geofences[igeofences];		                
                    var geofence_id                 =geofence["points"];
                    if(geofence["hidden"]==false)
                    {                        
                        var flightPlanCoordinates=array_points(geofence["points"]);                             
                        poligono(flightPlanCoordinates,{color:geofence["color"],geofence:geofence["name"]});	
                    }    
                }
            },1000);
        },
        //////////////////////////////////////////////////////////////
        geofences:function(){
            local.geofences=Array();
            var iresult;
            rpc.query({
                 model: "gpsmap.geofence", 
                 method: "search_read",
                 args:[[],[]],
            })
            .then(function (result) 
            {   
		        if(result!= null && result.length>0)
		        {
		            console.log("llena variable geocerca");
		            for(iresult in result)
		            {		                
		                var geofence                        =result[iresult];		                
                        var geofence_id                     =geofence["id"];                        
                        if(geofence["name"]!="")
                            local.geofences[geofence_id]    =geofence;                        
                    }
                }    
            });
        },
        //////////////////////////////////////////////////////////////
        positions_paint:function(argument)
        {               
            var ipositions;
            if(local.positions.length>0)
            {   
                console.log("POSITIONS PAINT ========");
                var vehiculo_id;
                var vehiculos       =local.vehicles;
                var ivehiculos;
                for(ipositions in local.positions)
                {	
                    var positions       =local.positions[ipositions];
                    var device_id       =positions.deviceid[0];                        
	                if(vehiculos!= null && vehiculos.length>0)
	                {	                    
	                    for(ivehiculos in vehiculos)
	                    {		                
	                        var vehiculo        =vehiculos[ivehiculos];		                
	                        
	                        if(vehiculo["id"]==device_id)
	                        {		                        
                                var vehiculo_name   =vehiculo["economic_number"];
                                var vehiculo_img    =vehiculo["image_vehicle"];

                                var coordinates		={"latitude":positions.latitude,"longitude":positions.longitude};
                                var posicion 		=LatLng(coordinates);
                                coordinates["ti"]   =positions.devicetime;
                                
                                if($("li.vehicle[vehicle='"+device_id+"']").length>0)                        
                                    $("li.vehicle[vehicle='"+device_id+"']").attr(coordinates);
             
	                            var v 	={
	                                mo: "", 
	                                st: "1", 
	                                te: "d_telefono",   
	                                dn: vehiculo_name,
	                                ty: positions.status,
	                                na: "name",
	                                de: device_id,
	                                la: positions.latitude,
	                                lo: positions.longitude, 
	                                co: positions.course, 
	                                mi: "milage", 
	                                sp: positions.speed_compu, 
	                                ba: "batery", 
	                                ti: positions.devicetime, 
	                                ho: "icon_online", 
	                                ad: positions.address, 
	                                //ot: positions.other, 
	                                im: vehiculo_img, 
	                                ev: positions.event, 
	                                ge: "geofence", 
	                                ni: "nivel"
                                };                                
                                
                                if(typeof argument=="number")
                                {
                                    v.se="historyForm";
                                }
                                
                                vehiculo["de"]=device_id;
                                vehiculo["dn"]=vehiculo_name,
                                vehiculo["la"]=positions.latitude;
                                vehiculo["lo"]=positions.longitude;
                                vehiculo["co"]=positions.course;
                                vehiculo["sp"]=positions.speed_compu;
                                vehiculo["ty"]=positions.status;
                                vehiculo["ti"]=positions.devicetime;
                                vehiculo["im"]=vehiculo_img;
                                
	                            locationsMap(vehiculo);            
	                            if(device_active==device_id) execute_streetMap(vehiculo);
                            }    
                        }
                    }            
                }
            }
        },
        //////////////////////////////////////////////////////////////
        positions_search:function(argument){
            console.log("POSITIONS SEARCH ========");
            var fields_select   =['deviceid','devicetime','latitude','longitude','speed_compu','attributes','address','event','status'];
            var vehiculo_id;
            var vehiculos       =local.vehicles;
            var iresult;
            var method;
            var time;
            var ivehiculos;
            
            if(typeof argument=="number")
            {
                method          ="read";
                arg             =[argument]
                time            =1000;
            }
            else
            {
                method          ="js_positions";
                time            =1;
            }
            
            setTimeout(function(){            
                if(vehiculos!= null && vehiculos.length>0)
                {	    
                    rpc.query({
                        model: 'gpsmap.positions',
                        method: method,
                        fields: fields_select,
                        order: 'devicetime DESC',
                    })
                    .then(function (result) 
                    {
                        del_locations();
                        local.positions=Array();                          
                        //if(result!= null && result.length>0)
                        {                            	            
                            for(iresult in result)
                            {
                                var positions               =result[iresult];
                                
                                var device                  =positions.deviceid;		                
                                var device_id               =device[0];
                                
                            	if(method=="read")          
                            	{
                            	    positions.se            ="historyForm";    
                            	    device_active           =device_id;
                            	}                   
                                positions.mo                ="";
                                positions.st                =1;
                                positions.te                ="d_telefono";
                                ////positions.dn                =vehiculo_name;
                                positions.ty                =positions.status;
                                positions.na                ="name";
                                positions.de                =device_id;
                                positions.la                =positions.latitude;
                                positions.lo                =positions.longitude; 
                                positions.co                =positions.course; 
                                positions.mi                ="milage"; 
                                positions.sp                =positions.speed_compu; 
                                positions.ba                ="batery"; 
                                positions.ti                =positions.devicetime; 

                                positions.ho                ="icon_online"; 
                                positions.ad                =positions.address; 
                                positions.at                =positions.attributes; 
                                ////positions.im                =vehiculos[device_id].image_vehicle; 
                                positions.ev                =positions.event; 
                                positions.ge                ="geofence"; 
                                positions.ni                ="nivel";
                                
                                local.positions[device_id]  =positions;
                            }                                    
                        }
                        gpsmaps_obj.positions_paint(argument);                                                              
                        //setTimeout(function(){            
                    });
                }
            },time);
                
        },

        //////////////////////////////////////////////////////////////
        CreateMap:function(iZoom,iMap,coordinates,object) 
        {
	        setTimeout(function()
	        {  
	            if(google!=null)
	            {                
	                console.log("Crear mapa");  
			        if(iMap=="ROADMAP")	            	var tMap = google.maps.MapTypeId.ROADMAP;
			        if(iMap=="HYBRID")	            	var tMap = google.maps.MapTypeId.HYBRID;								
			        var directionsService;	
			        
			        //maxZoomService 						= new google.maps.MaxZoomService();
			        var position		            	=LatLng(coordinates);
			        var mapOptions 		            	= new Object();
	        
			        if(iZoom!="")		            	mapOptions.zoom			=iZoom;
			        if(position!="")	            	mapOptions.center		=position;
			        if(iMap!="")		            	mapOptions.mapTypeId	=tMap;	            
			        
			        mapOptions.ScaleControlOptions		={position: google.maps.ControlPosition.TOP_RIGHT}
			        mapOptions.RotateControlOptions		={position: google.maps.ControlPosition.TOP_RIGHT}
			        mapOptions.zoomControlOptions		={position: google.maps.ControlPosition.TOP_LEFT};
			        mapOptions.streetViewControlOptions	={position: google.maps.ControlPosition.TOP_RIGHT}
			        				      
			        map    				                = new google.maps.Map(document.getElementById(object), mapOptions);        
			        geocoder 		   					= new google.maps.Geocoder();      
			        var trafficLayer 					= new google.maps.TrafficLayer();						
          			trafficLayer.setMap(map);
          					    
			        gMEvent                         	= google.maps.event;			        			        
			        
			        if($("div#odometro").length>0)
    			        $("div#odometro").hide();

                    return map;	        	
		        }
		        else return gpsmaps_obj.CreateMap(iZoom,iMap,coordinates,object);	   
	        },50);
        },
        //////////////////////////////////////////////////////////////
        map: function(object) {
            console.log("MAP ===========");
            if(object==undefined)   object="maponline";
	        var iZoom               =5;
	        var iMap                ="ROADMAP";
	        var coordinates         ={latitude:19.057522756727606,longitude:-104.29785901920393};
            gpsmaps_obj.CreateMap(iZoom,iMap,coordinates,object);                                   
        },

        //////////////////////////////////////////////////////////////
        vehicles:function(){
            local.vehicles=Array();
            var iresult;
            rpc.query({
                 model: "fleet.vehicle", 
                 method: "search_read",
                 args:[[],[]],
            })
            .then(function (result) 
            {   
		        if(result!= null && result.length>0)
		        {
		            console.log("llena variable vehiculo");
		            for(iresult in result)
		            {		                
		                var vehiculo                    =result[iresult];		                
                        var vehiculo_id                 =vehiculo["id"];                        
                        if(vehiculo["name"]!="")
                            local.vehicles[vehiculo_id]     =vehiculo;                        
                    }
                }    
            });
        },
        //////////////////////////////////////////////////////////////
		vehicles_menu: function(type)  
		{
            setTimeout(function()
            { 
		        var vehiculos       =local.vehicles;
		        var menu_vehiculo   ="";
		        var opcion_vehiculo ="";
		        var ivehiculos;
		        var icon;
		        		        
		        if(vehiculos!= null && vehiculos.length>0)
		        {
		            console.log("Crea menu de vehiculos con la variable");
		            for(ivehiculos in vehiculos)
		            {		                
		                var vehiculo        =vehiculos[ivehiculos];		                
                        var vehiculo_id     =vehiculo["id"];
                        var vehiculo_name   =vehiculo["license_plate"];
                        
                        if(!(vehiculo["economic_number"]==undefined || vehiculo["economic_number"]==false))
                        {
                            var vehiculo_name   =vehiculo["economic_number"];
                        }                        
                                                                        
			            var image="01";
			            if(!(vehiculo["image_vehicle"]==undefined || vehiculo["image_vehicle"]==false))
			            {
			                image=vehiculo["image_vehicle"];
			            }			
			            icon="/gpsmap/static/src/img/vehiculo_" +image+ "/i135.png";
		                opcion_vehiculo =opcion_vehiculo+"<li class=\"vehicle\" position=\"\" latitude=\"\" longitude=\"\" vehicle=\""+vehiculo_id+"\" style=\"padding-left:0px; padding-top:5px; padding-bottom:5px;\"><table width=\"100%\" class=\"select_devices\" device_id=\""+vehiculo_id+"\"><tr><td height=\"17\" width=\"50\" align=\"center\"><img height=\"17\" src=\"" +icon+ "\"></td><td>" + vehiculo_name + "</td><td  width=\"50\" align=\"center\" class=\"event_device\"> -</td></tr></table></li>";
		            }
                
		            if(!$("ul#menu_vehicles").length)	      
		            {
		                opcion_vehiculo ="<li class=\"vehicle vehicle_active\"  vehicle=\"0\" style=\"padding-left:0px; padding-top:5px; padding-bottom:5px;\"><table><tr><td height=\"15\" width=\"50\" align=\"center\"></td><td>Todos los vehiculos</td></tr></table></li>"+opcion_vehiculo;
		                opcion_vehiculo="<div class=\"oe_secondary_menu_section menu_soles\" id=\"vehiculos\">GPS Devices</div><ul class=\"oe_secondary_submenu nav nav-pills nav-stacked\" id=\"menu_vehicles\" style=\"display:block;\">"+opcion_vehiculo+"</ul>";
    
		                var opcion_vehiculo=opcion_vehiculo+"\
			                <script>\
			                    $(\"li.vehicle\").click(function(){\
    			                    $(\"li.vehicle\").removeClass(\"vehicle_active\");\
    			                    $(this).addClass(\"vehicle_active\");\
    			                    device_active               =$(this).attr(\"vehicle\");\
                                    status_device(this);\
			                    });\
			                </script>\
		                ";	
		                $("li > a > span:contains('Online'):last").parent().parent().append(opcion_vehiculo);  
		            }
		        }
		        else 
		        {
    		        gpsmaps_obj.vehicles_menu(type);		        
		        }    
            },50);
		},
        //////////////////////////////////////////////////////////////
        position: function(argument) {
            console.log("POSITION ========");
            //gpsmaps_obj.positions_search(argument);     
            setTimeout(function()
            {  
                if(argument==undefined)                 gpsmaps_obj.positions(argument);
                else if($("#data_tablero").length==0)   
                {
                    console.log("tablero");
                    gpsmaps_obj.position(argument);         
                }    
            },100);
        },
        ////////////////////////////////////////////////////////////
        positions: function(argument) {
            var time=1000;  	    
            if($("div#maponline").length>0) 
            { 
                console.log("POSITIONS ====== lalo =");
                time=40000;        
//                del_locations();
                gpsmaps_obj.positions_search(argument);         
            }
            if(typeof argument!="number")
            {
                setTimeout(function()
                {            
                    gpsmaps_obj.positions(argument);
                },time);
            }
        },    
        ////////////////////////////////////////////////////////////
        positions_online: function(argument) {
            local.vehicles  =Array();
            local.geofences =Array();
            local.positions =undefined;    

            status_device();
            gpsmaps_obj.vehicles();  
            gpsmaps_obj.geofences();
            gpsmaps_obj.positions_search();
            gpsmaps_obj.map();            
            
            gpsmaps_obj.vehicles_menu(argument);               
            var obj=$("li.vehicle_active")
            status_device(obj);
            gpsmaps_obj.geofences_paint();
            gpsmaps_obj.position();
        },    

    });
    
    //////////////////////////////////////////////////////////////
    ////////  GPSMAP_MAPONLINE  
    //////////////////////////////////////////////////////////////

    local.maponline = Widget.extend({
        template: 'gpsmaps_maponline',
        start: function() {       
            gpsmaps_obj.positions_online("gpsmaps_maponline");
        },
    });
    core.action_registry.add('gpsmap.maponline',local.maponline);

    //////////////////////////////////////////////////////////////
    ////////  GPSMAP_STREETONLINE  
    //////////////////////////////////////////////////////////////

    local.streetonline = Widget.extend({
        template: 'gpsmaps_streetonline',
        start: function() {
            gpsmaps_obj.positions_online("gpsmaps_streetonline");
            var panoramaOptions = {};
            
            var panorama = new google.maps.StreetViewPanorama(document.getElementById('street'), panoramaOptions);
            map.setStreetView(panorama);	                
        }
    });
    core.action_registry.add('gpsmap.streetonline', local.streetonline);
    gpsmaps_obj         =new class_gpsmap();  

    

    var FormController = require('web.FormController');
    var formController = FormController.include({
        _onButtonClicked: function (event) {
            if(event.data.attrs.id === "action_addpoint")
            {
                GeoMarker.push(coordinate);
                GeoMarker1.push(elocation);
                if(GeoMarker1.length>1)			
                {
                    puntos(GeoMarker);
                    polilinea(GeoMarker1);
                }
            }
            else if(event.data.attrs.id === "action_endpoint")
            {
                var point       =GeoMarker1[0];
                coordinate  =GeoMarker[0];
                GeoMarker.push(coordinate);
                GeoMarker1.push(point);		                
                polilinea(GeoMarker1);                			
                $("textarea[name='points']")
                    .focus()
                    .change();                    
                limpiar_virtual();				
            }
            else if(event.data.attrs.id === "action_clearpoint")
            {
                limpiar_virtual();
                limpiar_real();				         
            }
            else this._super(event);
        },
    });

});

	/*
	##################################################################
  	### FUNCIONES ESTANDAR
	##################################################################
	*/


	function foreach(datos)
	{
		for(i in datos)
		{				
			if(typeof datos[i]=="object")
			{   
			    //alert(i);
			    //*
			    
		        console.log(i + " (");             
			    foreach(datos[i]);
		        console.log(" )");             
		        //*/
			}
			else
			{
			    alert("  "+i + " = "+ datos[i]);
			    //console.log("  "+i + " = "+ datos[i]);             
			}	
		}		
	}
	
	/*
	##################################################################
  	### FUNCIONES GMAPS
	##################################################################
	*/
	
	function polilinea(LocationsLine,color)
	{	
		if(color==undefined)	var color="#FF0000";
		if(color=="") 			var color="#FF0000";
		
		Polyline = new google.maps.Polyline({
			path: LocationsLine,
			geodesic: true,
			strokeColor: color,
			
			strokeOpacity: 1.0,
			strokeWeight: 2
		});		
		Polyline.setMap(map);
		lineas.push(Polyline);
	} 
	function poligono(LocationsLine,option) 
	{	
		if(option==undefined)			option={};
		if(option.color==undefined)		option.color="#FF0000";		
		if(option.color=="") 			option.color="#FF0000";
		
		if(option.opacity==undefined)	option.opacity=0.8;		
		if(option.opacity=="") 			option.opacity=0.8;


		Polygon = new google.maps.Polygon({
			paths: LocationsLine,
			strokeColor: option.color,
			strokeOpacity: option.color,
			strokeWeight: 2,
			fillColor: option.color,
			fillOpacity: 0.35
		});	

		if(option.geofence!=undefined)
		{
			var total_lat=0;
			var total_lng=0;
			var may_lat=0;
			for(iLocationsLine in LocationsLine)
			{	
				if(LocationsLine[iLocationsLine].lat>may_lat)
				{ 
					may_lat= LocationsLine[iLocationsLine].lat
					may_lng= LocationsLine[iLocationsLine].lng
				}	
				
				total_lat =total_lat + LocationsLine[iLocationsLine].lat;
				total_lng =total_lng + LocationsLine[iLocationsLine].lng;																						
			}
			
			may_lat=may_lat - 0.00005;
			
			iLocationsLine			=parseInt(iLocationsLine)+1;
			
			var t_lat				=(total_lat / (iLocationsLine));
			var t_lng				=total_lng / (iLocationsLine);

			var posicion 		    = LatLng({latitude:t_lat,longitude:t_lng});						    	
		    
			var mapLabel = new MapLabel({
				text: 			option.geofence,
				position: 		posicion,
				map: 			map,
				fontSize: 		14,
				fontColor:		"#000000",
				align: 			"center",
				strokeWeight:	5,
			});
            
		}			
		
		Polygon.setMap(map);
	} 	   
	function map_info(objeto)  
	{
		return new google.maps.InfoWindow(objeto);				
	} 
	
	function LatLng(co)  
	{
		return new google.maps.LatLng(co.latitude,co.longitude);
	} 
    function centerMap(marcador)
	{
		map.panTo(marcador);		
	}
	function hablar(item)
	{
		var evento;
		if(!(item["ev"]==undefined || item["ev"]==false || item["ev"]=="false"))
        {        	
			evento 		= item["ev"];
			event		=evento.substring(0, 6);
		}			
		if(!(item["ev"]==undefined || item["ev"]==false || item["ev"]=="false" || event=="REPORT" || event=="Report"))
        {        
        	//var res = str.substring(1, 4);

			var obj=$("table.select_devices[device="+item["de"]+"]");

			device_active			=obj.attr("device");	
			
			//ajax_positions_now("../sitio_web/ajax/map_online.php");
			$(".select_devices").removeClass("device_active");
			$(obj).addClass("device_active");
		
		    status_device(obj);

        
            var fechaactual = item["ti"].split(" ");  
            	
        	var voz=item["dn"] + " reporta " + fechaactual[1];
        	if(!(item["ev"]==undefined || item["ev"]==false || item["ev"]=="false"))
        		voz=voz + ", " + item["ev"];
		    if(!(item["ad"]==undefined || item["ad"]==false || item["ad"]=="false"))       
				voz=voz + ", " + item["ad"];
				
				
		    	$("#message").html(voz)
		    	.dialog({
					show: {
						effect: "shake",
						duration: 750
					},		    			    	
		    		width:"350",
		    		modal: true,
		    	});
				setTimeout(function() 
				{
					$("#message").dialog("close")
				}, 2500 );

        	responsiveVoice.speak(voz,"Spanish Latin American Female");            	
        }		
	}
	
    function odometro(item)	 
    {    	
        if(item["at"]==undefined)           item["at"]=new Array();
    
    	if(item["at"]["battery"])			item["ba"]  =item["at"]["battery"];
    	else								item["ba"]  =0;
    	if(item["al"])						item["al"]  =item["al"];
    	else								item["al"]  =0;
    	
		//if(item["ot"]["battery"])			item["ga"]  =item["ot"]["battery"];
		var gas;
    	if(item["at"]["io3"]!=undefined)				
    	{
    		gas								=item["at"]["io3"];
    		item["ga"]  					=parseInt(gas.substring(0,3));
    	}	
    	else								item["ga"]  =0;
				    	    	    	    	

    	if(item["ba"]>100) item["ba"]=125;    
        var bat=item["ba"]*12/12.5-110;
        $("path.bateria").attr({"transform":"rotate("+ bat +" 250 250)"});            
        
        var vel=item["sp"]*12/10-110;  // 
        $("path.velocidad").attr({"transform":"rotate("+ vel +" 250 250)"});
        
        var alt=item["ga"]*12/10-38;
        $("path.altitude").attr({"transform":"rotate("+ alt +" 250 250)"});            

        $("#millas").html(item["mi"]);

        var tablero1="";
        var tablero2="";

		///*        
        if(item["st"]=="-1" && item["mo"]!="map")	//tiempo
        {
		    if(item["ni"]<=10)
	            tablero1= tablero1 + " :: EMPRESA PRE-BLOQUEADA :: ";
	        else
	        	alert("EMPRESA PRE-BLOQUEADA"); 
        }
        //*/
                        
        if(!(item["ti"]==undefined || item["ti"]==false || item["ti"]=="false"))	//tiempo
            tablero1= tablero1 + item["ti"];
        if(!(item["ge"]==undefined || item["ge"]==false || item["ge"]=="false"))        
            tablero1= tablero1 + " :: " + item["ge"];
  
        if(!(item["ev"]==undefined || item["ev"]==false || item["ev"]=="false"))	//evento
            tablero2= " :: " + item["ev"];
        
		
        if(!(item["ad"]==undefined || item["ad"]==false || item["ad"]=="false"))       
            tablero2= "UBICACION :: " + item["ad"] + tablero2;          
                       
        if(item["ni"]<=40)
        {
			var tablero="\
				<table>\
					<tr><td width=\"40\"  style=\"color:#fff;\"><a href=\"#\"onclick=\"command_device('Bloquear motor'," + item["de"] +")\"><img width=\"32\" src=\"../sitio_web/img/swich_off.png\"></a></td>\
					<td style=\"color:#fff;\"><a href=\"tel:" + item["te"] +"\">" + tablero1 + "</a></td></tr>\
					<tr><td width=\"40\"  style=\"color:#fff;\"><a href=\"#\"onclick=\"command_device('Activar motor'," + item["de"] +")\"><img width=\"32\" src=\"../sitio_web/img/swich_on.png\"></a></td>\
					<td style=\"color:#fff;\">" +tablero2 + "</td></tr>\
				</table>\
			";	
		}
		else
		{	
			var tablero="\
				<table id=\"data_tablero\">\
					<tr><td width=\"40\"  style=\"color:#fff;\"></td>\
					<td style=\"color:#fff;\">" + tablero1 + "</td></tr>\
					<tr><td width=\"40\"  style=\"color:#fff;\"></td>\
					<td style=\"color:#fff;\">" +tablero2 + "</td></tr>\
				</table>\
			";	
		}	
        $("#tablero").html(tablero);
    }

	function locationsMap(vehicle, type)
	{	
		if(type==undefined)     type="icon";
		else                    type="marker";

		if(vehicle["st"]==undefined)	vehicle["st"]="1";
		if(vehicle["st"]=="")			vehicle["st"]="1"; 
		if(vehicle["mo"]=="map")		vehicle["st"]="1";
		
		//alert(vehicle["mo"]);
	    //alert(vehicle["st"]);		
		if(vehicle["st"]=="1" || vehicle["st"]=="-1")
		{
			var device_id=vehicle["de"];
			
			if(localizacion_anterior==undefined)	
			{
				localizacion_anterior=new Array();				
				localizacion_anterior[device_id]={ti:"2000-01-01 00:00:01"}			
			}
			if(localizacion_anterior[device_id]==undefined)	
			{
				localizacion_anterior[device_id]={ti:"2000-01-01 00:00:01"}			
			}									
			if(vehicle["se"]=="historyMap" || vehicle["se"]=="historyForm" || vehicle["ti"] >= localizacion_anterior[device_id]["ti"])
			{
			    //alert("1");
				//if(vehicle["ti"] > localizacion_anterior[device_id]["ti"] && vehicle["se"]!="simulator")
				//	hablar(vehicle);
				localizacion_anterior[device_id]=vehicle;
			
				var coordinates			={latitude:vehicle["la"],longitude:vehicle["lo"]};
	
				$("table.select_devices[device="+ vehicle["de"] +"]")
					.attr("lat", vehicle["la"])
					.attr("lon", vehicle["lo"]);
					
				icon_status="";	
				if(vehicle["ty"]=="alarm")				                icon_status="sirena.png";
				if(vehicle["ty"]=="deviceStopped")		                icon_status="stop.png";
				if(vehicle["ty"]=="deviceMoving")		                icon_status="car_signal1.png";
				if(vehicle["ty"]=="deviceOnline")		                icon_status="car_signal1.png";
				if(vehicle["ty"]=="deviceOffline")		
				{
					icon_status="car_signal0.png";
					if(vehicle["ho"]==1)	                            icon_status="car_signal1.png";
				}	
				if(vehicle["ty"]=="ignitionOn")			                icon_status="swich_on.png";
				if(vehicle["ty"]=="ignitionOff")		                icon_status="swich_off.png";
				
				if(vehicle["sp"]<5 && vehicle["ty"]=="deviceOnline")	icon_status="stop.png";
				if(vehicle["sp"]>5 && vehicle["ty"]=="deviceOnline")	icon_status="car_signal1.png";
				
				if(icon_status!="")
				{				    
					img_icon="<img width=\"20\" title=\""+ vehicle["ty"] +"\" src=\"/gpsmap/static/src/img/"+ icon_status +"\" >";
					$("table.select_devices[device_id="+ vehicle["de"] +"] tr td.event_device").html(img_icon);
				}	
							
				var icon        		=undefined;
				
				var posicion 		    = LatLng(coordinates);						    	
				if(type=="icon")
				{				    
					var marcador;
					if(vehicle["co"]==undefined)        vehicle["co"]	=1;
					if(vehicle["co"])                   icon    		=vehicle["co"];
					
					if(icon>22 && icon<67)	icon=45;
					else if(icon<112)		icon=90;
					else if(icon<157)		icon=135;
					else if(icon<202)		icon=180;
					else if(icon<247)		icon=225;
					else if(icon<292)		icon=270;
					else if(icon<337)		icon=315;
					else					icon=0;		

					var image="01";
					if(!(vehicle["im"]==undefined || vehicle["im"]==false))		image	=vehicle["im"];

					//icon	="../sitio_web/img/car/vehiculo_" +image+ "/i"+icon+ ".png";		    
					icon="/gpsmap/static/src/img/vehiculo_" +image+ "/i"+icon+ ".png";		    
					if(labels[device_id]==undefined)	
					{

						labels[device_id]=new MapLabel({
							text: 			vehicle["dn"],
							position: 		posicion,
							map: 			map,
							fontSize: 		14,
							fontColor:		"#8B0000",
							align: 			"center",
							strokeWeight:	5,
						});
						
					}
					//alert("2");
					labels[device_id].set('position', posicion);
			
					if(device_active==vehicle["de"] && vehicle["se"]==undefined || vehicle["se"]=="simulator" || vehicle["se"]=="historyForm") 
					{
					    centerMap(posicion);			
					    odometro(vehicle);
					} 
				}				
				var marcador 		    = markerMap(posicion, icon);		
					
				//var infowindow 		    = messageMap(marcador, vehicle);	
				fn_localizaciones(marcador, vehicle);
			}
			else
			{
				//alert(vehicle["ti"] + ">"+ localizacion_anterior[device_id]["ti"]);
			}					
		}
		else 
		{
			var marcador 		    =undefined;
			
			var tablero="<table><tr><td style=\"color:red;\"><b>Los vehiculos se encuentran bloqueados</b></td></tr><tr><td style=\"color:#fff;\">Favor de contactar con el administrador del sistema</td></tr></table>";	
    	    $("#tablero").html(tablero);			
		}
		return marcador;
	}
	function markerMap(position, icon, markerOptions) 
	{
		if(markerOptions==undefined)	var markerOptions 			= new Object();
				
		markerOptions.position		=position;
		markerOptions.map			=map;
		if(icon!=undefined)
			markerOptions.icon		=icon;
				
		var marker2=new google.maps.Marker(markerOptions);
 		return marker2
	}
    function codeAddress(address,city,country) 
    {
    	var txt_address="";
    	if(country!=undefined)	txt_address+=country+", ";
    	if(city!=undefined)		txt_address+=city+", ";
    	if(address!=undefined)	txt_address+=address;
    	
        geocoder.geocode({'address': txt_address}, 
        function(results, status) 
        {
            if (status == google.maps.GeocoderStatus.OK) 
            {
                map.setCenter(results[0].geometry.location);
                map.setZoom(17);

                markerMap(results[0].geometry.location,undefined);
            } 
            else 	alert('Geocode was not successful for the following reason: ' + status);

        });
    }
    
    function fn_localizaciones(position, vehiculo)
    {
    	var ivehiculo=vehiculo["de"];
		if(localizaciones[ivehiculo]==undefined)     	
		{
			localizaciones[ivehiculo]	=Array(position);
			if(vehiculo["se"]!="simulator")    	vehicle_data[ivehiculo]		=Array(vehiculo)
		}	
		else
		{
			localizaciones[ivehiculo].unshift(position);			
			if(vehiculo["se"]!="simulator")     vehicle_data[ivehiculo].unshift(vehiculo)
		}	
    }    
	function del_locations(borrar)  
	{			    
		if(borrar==undefined)	borrar="si";
        if(localizaciones.length>0)                
        {
            for(idvehicle in localizaciones)
            {
                var positions_vehicle			= localizaciones[idvehicle];                    
                if(positions_vehicle.length>0)                
                {
                    for(iposiciones in positions_vehicle)
                    {    
                        //if(iposiciones>0)
                        {	
	                    	localizaciones[idvehicle][iposiciones].setVisible(false);								
                    		localizaciones[idvehicle][iposiciones].setMap(null);                     
                        	//if(iposiciones>0)	                        	localizaciones[idvehicle]=[]; 
	                    } 	                    
                    }                    
                }
            }

        }
        
	}
	function array_points(points) 
	{
	    var array_points=new Array();
        var vec_points  =points.split("|");
        for(i_vec_points in vec_points)
        {                   
            var point       =vec_points[i_vec_points];
            if(point!="")
            {                
                var vec_point   =point.split(",");	                   
                var obj_point={lat:parseFloat(vec_point[1]),lng:parseFloat(vec_point[0])};
                array_points.push(obj_point);
            }
        }        
       return array_points;
	}
	function messageMaps(marcador, vehicle, infowindow) 
	{
		gMEvent.addListener(marcador, 'click', function() 
		{
		    device_active=vehicle["de"];
		    		    		    
			$(".select_devices").removeClass("device_active");
			$(".select_devices[device="+ vehicle["de"] +"]").addClass("device_active");			
			
			if(vehicle["se"]=="historyMap")	infowindow.open(map,marcador);
			else							status_device();
		});							
	}
	function paint_history(iposiciones, section)
	{			    
        if(vehicle_data[device_active].length>isimulacion)                
        {        	
        	localizacion_anterior=undefined;
	    	var vehicle			=vehicle_data[device_active][isimulacion];	    	
	    		    	
	    	if(vehicle["sp"]>4)	
	    	{
	    		simulation_stop=0;
	    		simulation_time=600;
	    	}	
	    	else	
	    	{
					if(simulation_stop<20)
					{
						simulation_stop=simulation_stop+1;
						if(simulation_time==600)    simulation_time=300;
					}	
					else
					{
						if(simulation_time==300)	simulation_time=5;
					}	
	    	}	
	    	
	    	vehicle["se"]		="simulator";
	    	locationsMap(vehicle); 
	    	if(section=="historyStreet")			execute_streetMap(vehicle);
            setTimeout(function()
            {   
            	if(simulation_action!="pause")		                                            		    	
	            	del_locations();
            	isimulacion=isimulacion+1;
            	if(simulation_action=="play")		
            		paint_history(isimulacion, section);
            },simulation_time);
        }
	}
/*
	function dateTimes()
	{
		$('#fInicio').datetimepicker({
			dateFormat: "yy-mm-dd",
			timeFormat: 'HH:mm:ss',
			changeMonth: false,
			changeYear: false,
			currentText: "Ahora",
			closeText: "Listo",
			showSecond: false,			
			showMillisec:false,
			showMicrosec:false,
			showTimezone:false,
			dayNamesMin: ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"],
			monthNames: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
			monthNamesShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
		});

		$('#fFinal').datetimepicker({
			dateFormat: "yy-mm-dd",
			timeFormat: 'HH:mm:ss',
			changeMonth: false,
			changeYear: false,
			currentText: "Ahora",
			closeText: "Listo",
			showSecond: false,			
			showMillisec:false,
			showMicrosec:false,
			showTimezone:false,
			dayNamesMin: ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"],
			monthNames: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
			monthNamesShort: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
		});	
		
	}
*/
	function butons_simulation()
	{
		var butons_html=" \
			<font id=\"back\"> -- </font>\
			<font id=\"play\">Play</font>\
			<font id=\"pause\">Pause</font>\
			<font id=\"stop\">Stop</font>\
			<font id=\"next\"> ++ </font>\
		";
		$("#tablero2").html(butons_html);
		$("#tablero").html("");
	
	    $("#play").button({
			icons: {
				primary: "ui-icon-play"
			},
			text: false
			})
			.click(function()
			{			    
				if(localizaciones.length>0)                
				{
				    simulation_action="play";
				    del_locations();
				    $("div#odometro").show();
					paint_history(isimulacion, historyMap);
				}    					
			}
		);
	    $("#pause").button({
			icons: {
				primary: "ui-icon-pause"
			},
			text: false
			})
			.click(function()
			{			    
			    simulation_action="pause";
			}
		);
		
	    $("#next").button({
			icons: {
				primary: "ui-icon-seek-next"
			},
			text: false
			})
			.click(function()
			{
				if(simulation_time>=50)
					simulation_time=simulation_time-50;
			}
		);
	    $("#back").button({
			icons: {
				primary: "ui-icon-seek-prev"
			},
			text: false
			})
			.click(function()
			{
				simulation_time=simulation_time+50;
			}
		);				
	    $("#stop").button({
			icons: {
				primary: "ui-icon-stop"
			},
			text: false
			})
			.click(function()
			{
				isimulacion=1;
				simulation_action="stop";
			}
		);		
	
	}
	
	
    function status_device(obj)
    {	    	
        console.log("STATUS DEVICE ==========");
        if(device_active==undefined)    device_active	=0;        
        if(obj!=undefined)
        {	            
            var latitude                =$(obj).attr("latitude");
            var longitude               =$(obj).attr("longitude");

            if(latitude!=undefined)
            {
                console.log("Pinta coordenadas");
                var coordinates             ={"latitude":latitude,"longitude":longitude};
                var position                = LatLng(coordinates);
                map.panTo(position);
            }
        }    
		if(device_active==0)	
		{		 
		    if($("div#odometro").length>0)
		    {   
			    $("div#map_search").show();
			    $("div#odometro").hide();
			    $("#tablero").html("Estatus : Seleccionar un vehiculo");			
			    $("#tablero").animate({				
				    height: 25
			    }, 1000 );			
		    }
		}	
		else
		{
			map.setZoom(16);
            if($("div#odometro").length>0)
            {
			    $("#tablero").animate({				
				    height: 58
			    }, 1000 );
			    $("#tablero").html("<h5>Cargando...</h4><img id=\"loader1\" src=\"../sitio_web/img/loader1.gif\" height=\"20\" width=\"20\"/>");	
			    //status_device2();
			    $("#odometro").show(); 
			    $("div#map_search").hide();
	        }
		}	  			
	}
	
	function execute_streetMap(vehicle)
	{
		if($("div#street").length>0)
		{
			var coordinates						={latitude:vehicle["la"],longitude:vehicle["lo"]};
		
			if(coordinate_active==undefined)	coordinate_active={};
			var txt_active						=coordinate_active["latitude"]+","+coordinate_active["longitude"];
			var txt_history						=coordinates["latitude"]+","+coordinates["longitude"];

			var txt 							= txt_active + " " +txt_history;
		
			if(txt_active!=txt_history)
			{	
				coordinate_active				=coordinates;
				var posicion					=LatLng(coordinates);
				
				centerMap(posicion);
				var curso           			=vehicle["co"];		        
				var panoramaOptions = {
				    position: posicion,
				    pov: {
				      heading:  curso,
				      pitch:    10
				    }
				};
				
				var panorama = new google.maps.StreetViewPanorama(document.getElementById('street'), panoramaOptions);
				map.setStreetView(panorama);	                		    
			}        
		}	
	}
	function serializar_url(url)
	{
		var arrUrl 	= url.split("&");
		//var varrUrl	= arrUrl.splice(0, 1); 
		
		var urlObj	={};   
		for(var i=0; i<arrUrl.length; i++)
		{
			var x			= arrUrl[i].split("=");
			urlObj[x[0]]	=x[1]
		}
		return urlObj;	
	}	

	function command_device(comando,device_id)
	{
		var r = confirm(comando);
		if (r == true) 
		{
			if(comando=="Bloquear motor") 	comando="engineStop";
			if(comando=="Activar motor")	comando="engineResume";
						
			$.ajax({
				type: 'POST',
				url: 'http://solesgps.com:8082/api/commands',
				headers: {
					"Authorization": "Basic " + btoa("admin:EvG30")
				},
				contentType:"application/json",
				data:JSON.stringify({attributes:{},deviceId:device_id,type:comando}),
				success: function (response) 
				{
					console.log(response);
				}
			});
		} 				
	}	
	function puntos(GeoMarker)
    {
		var punto	=new String();
		var puntos	=new String();
		for(index in GeoMarker)
		{		
			punto	=GeoMarker[index];
			puntos	+=punto["latitude"]+","+punto["longitude"]+"|"; 
			console.log("field points="+puntos);    			
		    $("textarea[name='points']").val(puntos);
		}
		return puntos;
	}
	function limpiar_virtual()
	{		
		for(indexMarker=0;indexMarker<locationsMarker.length;indexMarker++)
		{
			locationsMarker[indexMarker].setMap(null);			
		}				
		locationsMarker.length = 0;		
		locationsMarker=Array();
	}
	function limpiar_real()
	{	
		limpiar_virtual();
		$("input#points").val("");		
		for(ilineas in lineas)
		{			
			lineas[ilineas].setMap(null);									
		}
		lineas		=Array();	
		GeoMarker	=Array();
		GeoMarker1	=Array();
	}
