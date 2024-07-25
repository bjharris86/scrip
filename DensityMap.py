import arcpy,datetime,os,shutil,subprocess,time
from arcpy import env
from arcpy.sa import *


arcpy.CheckOutExtension("spatial")
subprocess.call('sqlcmd -S pdrmscvpr16 -d sandbox -Q "exec dbo.sp_8wk_HotSpots"')

outputfolder = r"C:\Automated_Maps_Projects\Rolling_8wk\Maps"
layerfolder = r"C:\Automated_Maps_Projects\Rolling_8wk\Layers"
left_folder_path = r"C:\Automated_Maps_Projects\Rolling_8wk\Layers\Prior_4"
right_folder_path = r"C:\Automated_Maps_Projects\Rolling_8wk\Layers\Last_4"
thegdb = r"C:\Automated_Maps_Projects\Rolling_8wk\Rolling_8wk.gdb"
aprx = arcpy.mp.ArcGISProject(r"C:\Automated_Maps_Projects\Rolling_8wk\Rolling_8wk.aprx")
layout = aprx.listLayouts('Layout')[0] #first layout named Layout
ml = aprx.listMaps('Prior 4wks')[0]  #map frame named Prior 4 wks
mr = aprx.listMaps('Last 4wks')[0]  #map frame named Last 4 wks
wrk = aprx.listMaps('Work')[0] #map fram named Work - used for a scratch workspace
layout_title = layout.listElements("text_element", "title")[0]


theprojection   = "PROJCS['NAD_1983_StatePlane_Tennessee_FIPS_4100_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-86.0],PARAMETER['Standard_Parallel_1',35.25],PARAMETER['Standard_Parallel_2',36.41666666666666],PARAMETER['Latitude_Of_Origin',34.33333333333334],UNIT['Foot_US',0.3048006096012192]]"
arcpy.env.overwriteOutput = True
arcpy.env.workspace = thegdb
arcpy.env.scratchWorkspace = thegdb
arcpy.env.extent = "1656911.98574869 596061.18018044 1819512.79034007 755283.98753397"
templatelyr = r"C:\Automated_Maps_Projects\Rolling_8wk\Template.lyrx" 

print('Grid Shading Template: '+templatelyr)

sandbox = "C:\\Users\\bjharris\\Desktop\\Python Project Source\\Auto Map Projects\\Automated_Maps_Projects\\Rolling_8wk\\pdrmscvpr16_sandbox.sde\\"
#layout_extent = arcpy.env.extent = (1656911.98574869, 596061.18018044, 1819512.79034007, 755283.98753397)


def customize_title(layer_name):
    custom_titles = {
        "Agg_Assault_Prv_4wks": "MNPD Aggravated Assault \n 1 Mile Kernel Density",
        "Comm_Burglary_Prv_4wks": "MNPD Commercial Burglary \n 1 Mile Kernel Density",
        "Comm_Robbery_Prv_4wks": "MNPD Commercial Robbery \n 1 Mile Kernel Density",
        "MVT_Prv_4wks": "MNPD Motor Vehicle Theft \n 1 Mile Kernel Density",
        "Res_Burglary_Prv_4wks": "MNPD Residential Burglary \n 1 Mile Kernel Density",
        "Str_Robbery_Prv_4wks": "MNPD Street Robbery \n 1 Mile Kernel Density",
        "Theft_From_MV_Prv_4wks": "MNPD Theft From Motor Vehicle \n 1 Mile Kernel Density"
    }
    return custom_titles.get(layer_name, "MNPD 1 Mile Kernel Density")
def deletefile(thefile):
    if arcpy.Exists(thefile):
        arcpy.Delete_management(thefile)

def reclass(ingrid,outgrid):
    # Get minimum and maximum cell values of the grid
    maxcellval = float(str(arcpy.GetRasterProperties_management(ingrid, "MAXIMUM")))
    mincellval = 0
    numclasses = 9
    rangesize = (maxcellval- mincellval)/numclasses
    classlist = range(1, numclasses+1, 1)
    # Choose range that will be assigned a NODATA value (values <= 1)
    #reclassstr = "0 1 NODATA;"
    #reclassstr = "0 1 1;"
    reclassstr=""
    lowval = mincellval
    for cls in classlist:
        hival = lowval + rangesize
        reclassstr = reclassstr + str(lowval) + " " + str(hival) + " " + str(cls) + ";"
        lowval = hival
    reclassstr = reclassstr[:-1]
    if maxcellval == 0:
        # If the grid only has a maximum value of zero then don't reclassify it
        arcpy.CopyRaster_management (ingrid, outgrid)
    else:
        # Process: Reclassify...
        thegrid = Reclassify(ingrid, "Value", reclassstr, "DATA")
        thegrid.save(outgrid)
    arcpy.BuildPyramids_management(outgrid)
    deletefile(ingrid)
# Function to export layout to PDF
def export_layout_to_pdf(aprx,layout_name, outputfolder, output_name):
    layout = aprx.listLayouts(layout_name)[0]
    pdf_export_path = os.path.join(outputfolder, f"{output_name}.pdf")
    layout.exportToPDF(pdf_export_path)
    print(f"Exported layout to: {pdf_export_path}")


vallist = ['Comm_Robbery_Pst_4wks'
          ,'Comm_Robbery_Prv_4wks' 
          ,'Str_Robbery_Pst_4wks'
          ,'Str_Robbery_Prv_4wks'
          ,'Agg_Assault_Pst_4wks'
          ,'Agg_Assault_Prv_4wks' 
          ,'Comm_Burglary_Pst_4wks'
          ,'Comm_Burglary_Prv_4wks'
          ,'Res_Burglary_Pst_4wks'
          ,'Res_Burglary_Prv_4wks'
          ,'Theft_From_MV_Pst_4wks'
          ,'Theft_From_MV_Prv_4wks'
          ,'MVT_Pst_4wks'
          ,'MVT_Prv_4wks'
                   
]


for val in vallist: 
    print (sandbox+val)
    print (thegdb+"\\d_"+val)
    sqltable = sandbox+"dbo."+val
    denslayer = thegdb+"\\d_"+val 
    denslayer1 = thegdb+"\\d1_"+val
    templayer = "templyr"
    new_layer= val.replace('_',' ')
    try:
        arcpy.management.Delete(denslayer)
    except:
        pass
    arcpy.management.MakeXYEventLayer(sqltable,"i_x","i_y",templayer, theprojection,"")
    # --- ONE MILE --- 
    outkdens = KernelDensity(templayer,"NONE","25","5280","SQUARE_MILES","DENSITIES","PLANAR")
    # --- HALF MILE --- 
    #KernelDensity(templayer,"NONE","25","2640","SQUARE_MILES","DENSITIES","PLANAR")
    # --- QUARTER MILE --- 
    #KernelDensity(templayer,"NONE","25","1320","SQUARE_MILES","DENSITIES","PLANAR")
    # --- EIGHTH MILE --- 
    #KernelDensity(templayer,"NONE","25","660","SQUARE_MILES","DENSITIES","PLANAR")
    outkdens.save(denslayer)
    arcpy.management.BuildPyramids(denslayer)
    reclass(denslayer,denslayer1)
    print ('Layers Reclassified...')
    try:    
        if val[-8:-5] == "Pst": arcpy.management.SaveToLayerFile(arcpy.ApplySymbologyFromLayer_management(denslayer1, templatelyr), (layerfolder+"\\Last_4\\"+f"{val}.lyrx")) 
        else: arcpy.management.SaveToLayerFile(arcpy.ApplySymbologyFromLayer_management(denslayer1, templatelyr),layerfolder+"\\Prior_4\\"+f"{val}.lyrx" )
    except:
        pass
    
    print("Density completed and sent to folders")
    
    # Remove 
 
    
    deletefile(denslayer)
    deletefile(templayer)
    
    
    
    print("Layers have been destroyed forever, don't even mention them")
    print ("Process Complete for "+ f"{val}!")

# List all layers in folder
left_layers = [os.path.splitext(layer)[0] for layer in os.listdir(left_folder_path) if layer.endswith(".lyrx")]
right_layers = [os.path.splitext(layer)[0] for layer in os.listdir(right_folder_path) if layer.endswith(".lyrx")]



print(left_layers)
print("forming final layout")


# Iterate through layer pairs and create layout



for left_layer,right_layer in zip(left_layers, right_layers):
    try:
        # Add layers to maps
        left_layer_path = os.path.join(left_folder_path, f"{left_layer}.lyrx")
        right_layer_path = os.path.join(right_folder_path, f"{right_layer}.lyrx")
        
        
        ml.addDataFromPath(left_layer_path)
        mr.addDataFromPath(right_layer_path)
        
        print("adding "+left_folder_path+ "\\"+f"{left_layer}")
        time.sleep(1)
        # Customize title based on layers added
        #combined_title = customize_title(left_layer)  # Assuming left_layer and right_layer are similar

        # Access layout of left map (assuming they have the same layout)
            
        title = customize_title(left_layer)
        layout_title.text = title
        print(layout_title)
        print(left_layer)

        # Export layout to PDF
        export_layout_to_pdf(aprx, "Layout",outputfolder, title[5:title.find('\n')])
        print("exporting "+f"{left_layer}_and_{right_layer}_Density "+"layout to pdf to "+ outputfolder)
       
        print("Map complete for  "+f"{left_layer}")
    except Exception as e:
        print(f"An error ocurred: {str(e)}")

    finally:
         # Remove layers from maps to prepare for next iteration
        print(f"removing  {ml.listLayers()[-1]}")
        print(f"removing  {mr.listLayers()[-1]}")
        ml.removeLayer(ml.listLayers()[-1])
        mr.removeLayer(mr.listLayers()[-1])
        
        time.sleep(1)


print("This is the end. Good Day.")
