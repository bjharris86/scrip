import arcpy, os, shutil, time, subprocess,time



# Set your lyrx folder, output folder, and SQL table
lyrx_folder = r"C:\Users\bjharris\Desktop\Maps\DV_Layers"
output_folder = r"C:\Users\bjharris\Desktop\Maps\Automated_maps"

# Defined fixed extents for each layout
layout_extents = {
    "1": arcpy.Extent(689461.8719978293, 1653697.9554737706, 1731701.1001278588, 597094.7336330495),
    "2": arcpy.Extent(697370.9486053591, 1736055.30032842, 1765609.078106198, 663721.1708275813),
    "3": arcpy.Extent(678377.5571892178, 1731705.9558290232, 1820995.0183290232, 576713.4946892178),
    "4": arcpy.Extent(677654.8462992206, 1731366.0033590258, 1746346.2222390259, 660598.4469392207),
    "5": arcpy.Extent(721927.5621246237, 1736145.2310084691, 1825434.2935084691, 620263.4996246237),
    "6": arcpy.Extent(753122.8746246237, 1667481.1685084691, 1756770.2310084691, 651458.8121246237),
    "7": arcpy.Extent(759336.5402180236, 1703381.3035461982, 1802874.6368795317, 673108.9846624681),
    "8": arcpy.Extent(671529.3947785723, 1711320.8647679773, 1768465.8647679773, 606464.3947785723),
    "0": arcpy.Extent(765202.8486902476, 1643946.6159073035, 1828838.108962859, 554686.3556346921)
}

    
# Function to export layout as PNG, overwriting existing files
def export_layout_as_png(layout, output_path):
    if os.path.exists(output_path):
        os.remove(output_path)
    layout.exportToPNG(output_path, resolution=300)

    
# Function to add layer to map and export layout
def process_lyr(lyr_file, lyr_name):
    #  Map project
    aprx = arcpy.mp.ArcGISProject(r"O:\ArcPro\This\DV_Map\DV.aprx")
    map = aprx.listMaps()[0]  # Assuming only one map exists in the project

    # Add layer to map
    lyr = map.addDataFromPath(os.path.join(lyrx_folder, lyr_file))
    
    # Ensure layer visibility
    lyr.visible = True

    # Loop through layouts
    for layout in aprx.listLayouts():
        # Set layout extent based on layout name
        layout_extent = layout_extents.get(layout.name)
        if layout_extent:
            lyr.visible = True  # Ensure layer is visible on layout
            map.extent = layout_extent  # Set extent for layout


            # Export layout as PNG, overwriting existing files
            output_path = os.path.join(output_folder,lyr_name, f"{layout.name}.png")
            export_layout_as_png(layout, output_path)

            # Insert exported file path into SQL table
            sql_output_path = fullsql+"\\"+f"{layout.name}.png"
            
            export_layout_as_png(layout, sql_output_path)

            lyr.visible = False  # Turn off layer after exporting layout
            sql="""
            \"
            delete dbo.automated_maps where report='{0}' and precinct = '{1}'
            insert into dbo.automated_maps (report, precinct, sdd_updated_on, graphic) select '{0}','{1}',getdate(), bulkcolumn from OPENROWSET (BULK N'\\\\pdrmscvpr16\\sdd_images\\automated_maps\\{0}\\{1}.png',SINGLE_BLOB) as x
            \"
            """.format(os.path.splitext(lyrx_file)[0],layout.name)
            print(sql)
            #print('start sleep '+layout.name)
            #time.sleep(1)
            subprocess.call('sqlcmd -S pdrmscvpr16 -d sddca -Q '+sql)
            #print('end sleep '+layout.name)


    # Remove layer from map
    map.removeLayer(lyr)

    del aprx




# Loop through lyrx files
for lyrx_file in os.listdir(lyrx_folder):
    fullpath = os.path.splitext(output_folder+lyrx_file)[0]
    print("local datastore: "+fullpath)
    sqlpath = '\\\\pdrmscvpr16\\sdd_images\\automated_maps\\' 
    fullsql= os.path.splitext(sqlpath+lyrx_file)[0]
    print("sql datastore"+ ""+sqlpath)

    if lyrx_file.endswith(".lyrx"):
        lyr_name = os.path.splitext(lyrx_file)[0]
        # Create subfolder for the lyrx file if not exists
        subfolder_path = os.path.join(output_folder, lyr_name)
        if os.path.exists(subfolder_path):
            shutil.rmtree(subfolder_path)
        os.makedirs(subfolder_path)
        process_lyr(lyrx_file, lyr_name)
