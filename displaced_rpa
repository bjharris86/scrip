import arcpy,datetime,os,shutil,subprocess,time
from arcpy import env
from arcpy.sa import *


arcpy.CheckOutExtension("spatial")


outputfolder = r"C:\Users\bjharris\Desktop\Maps\Automated_maps"
#layerfolder = r"C:\Automated_Maps_Projects\Rolling_8wk\Layers"
thegdb = r"C:\Automated_Maps_Projects\Rolling_8wk\Rolling_8wk.gdb"
aprx = arcpy.mp.ArcGISProject(r"C:\Users\bjharris\Desktop\Maps\displaced.aprx")
layout = aprx.listLayouts()[0] #first layout named 0 for countywide
m= aprx.listMaps('Map')[0]  #map frame named Map


dis = "displaced_rpa"
theprojection   = "PROJCS['NAD_1983_StatePlane_Tennessee_FIPS_4100_Feet',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',1968500.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-86.0],PARAMETER['Standard_Parallel_1',35.25],PARAMETER['Standard_Parallel_2',36.41666666666666],PARAMETER['Latitude_Of_Origin',34.33333333333334],UNIT['Foot_US',0.3048006096012192]]"
arcpy.env.overwriteOutput = True
arcpy.env.workspace = thegdb
arcpy.env.scratchWorkspace = thegdb
arcpy.env.extent = "1656911.98574869 596061.18018044 1819512.79034007 755283.98753397"

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



def deletefile(thefile):
    if arcpy.Exists(thefile):
        arcpy.Delete_management(thefile)

# Function to export layout to PDF
def export_layout_as_png(layout, output_path):
    if os.path.exists(output_path):
        os.remove(output_path)
    layout.exportToPNG(output_path, resolution=300)



for lyt in aprx.listLayouts():
    layout_extent = layout_extents.get(lyt.name)
    
    if layout_extent:    
        m.extent = layout_extent
        #map.extent = layout_extent  # Set extent for layout
        fullpath = os.path.join(outputfolder,dis)
        print("local datastore: "+fullpath)
        sqlpath = '\\\\pdrmscvpr16\\sdd_images\\automated_maps\\' 
        fullsql= os.path.join(sqlpath,dis)
        print("sql datastore"+ ""+sqlpath)
        subfolder_path = os.path.join(outputfolder, dis)
        if os.path.exists(subfolder_path):
            shutil.rmtree(subfolder_path)
            os.makedirs(subfolder_path)
            # Export layout as PNG, overwriting existing files
        output_path = os.path.join(outputfolder,dis, f"{lyt.name}.png")
        export_layout_as_png(lyt, output_path)

        # Insert exported file path into SQL table
        sql_output_path = fullsql+"\\"+f"{lyt.name}.png"
                        
        export_layout_as_png(lyt, sql_output_path)

                        
        sql="""
                \"
                delete dbo.automated_maps where report='{0}' and precinct = '{1}'
                insert into dbo.automated_maps (report, precinct, sdd_updated_on, graphic) select '{0}','{1}',getdate(), bulkcolumn from OPENROWSET (BULK N'\\\\pdrmscvpr16\\sdd_images\\automated_maps\\{0}\\{1}.png',SINGLE_BLOB) as x
                \"
                """.format(dis,lyt.name)
        print(sql)
                        #print('start sleep '+layout.name)
                        #time.sleep(1)
        subprocess.call('sqlcmd -S pdrmscvpr16 -d sddca -Q '+sql)
                        #print('end sleep '+layout.name)







print("This is the end. Good Day.")
