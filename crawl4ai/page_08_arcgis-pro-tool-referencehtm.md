# ArcGIS Pro Content - Page 8

**Source URL:** https://pro.arcgis.com/en/pro-app/latest/tool-reference/main/arcgis-pro-tool-reference.htm

**Page Type:** linked_page

---

ArcGIS Pro geoprocessing tool reference

Anatomy of a tool reference page

3D Analyst toolbox

AllSource toolbox

Analysis toolbox

Aviation toolbox

Bathymetry toolbox

Business Analyst toolbox

Cartography toolbox

Conversion toolbox

Crime Analysis and Safety toolbox

Data Interoperability toolbox

Data Management toolbox

Data Reviewer toolbox

Defense toolbox

Editing toolbox

GeoAI toolbox

GeoAnalytics Desktop toolbox

GeoAnalytics Server toolbox

Geocoding toolbox

Geostatistical Analyst toolbox

Image Analyst toolbox

Indoors toolbox

Indoor Positioning toolbox

Linear Referencing toolbox

Location Referencing toolbox

Maritime toolbox

Multidimension toolbox

Network Analyst toolbox

Network Diagram toolbox

Oriented Imagery toolbox

Parcel toolbox

Public Transit toolbox

Raster Analysis toolbox

Ready To Use toolbox

Reality Mapping toolbox

Server toolbox

Space Time Pattern Mining toolbox

Spatial Analyst toolbox

Spatial Statistics toolbox

Standard Feature Analysis toolbox

Territory Design toolbox

Topographic Production toolbox

Trace Network toolbox

Utility Network toolbox

Environments

Appendices

Geoprocessing tool reference content

The ArcGIS Pro geoprocessing tool reference contains detailed information about every geoprocessing tool provided with ArcGIS Pro as well as the environment settings that can be applied to them and any errors or warnings that may be encountered as you use them.

What is geoprocessing?

Geoprocessing quick tour

Spatial analysis in ArcGIS Pro

Use a tool

If working with tools in ArcGIS Pro is new to you or you want to understand how the tools fit within the context of the geoprocessing framework, start with the What is geoprocessing topic.

If you're familiar with tools, you can review how to run the tools using the Geoprocessing pane, ModelBuilder, and Python.

You can run the tools with the following:

Run a tool in the Geoprocessing pane

To run a tool in the Geoprocessing pane, complete the following steps:

On the Analysis ribbon, click the Tools button. The Geoprocessing pane appears.

Select a tool to open it in the pane.

Set input and output parameters. Required parameters must be filled in for the tool to run and are indicated by a red asterisk. Optional parameters can be left blank or unmodified to use a default behavior.

Optionally, select the Environments tab. If an environment setting is modified, it will only be applied to this specific instance of the tool.

Click the Run button.

For more details, see Find a geoprocessing tool and Run a geoprocessing tool.

Run a tool in ModelBuilder

To run a tool in ModelBuilder, complete the following steps:

On the Analysis tab, click the ModelBuilder button. A blank canvas opens for the new model.

Drag a tool onto the model from the Geoprocessing or Catalog pane. You can also drag additional elements onto the model, such as data, map layers, or more tools.

Set the input and output parameters for the tool to connect your data. Required parameters must be filled in for the tool to run and are indicated by a red asterisk. Optional parameters can be left blank or unmodified to use a default behavior.

Optionally, select the Environments tab. If an environment setting is modified, it will only be applied to this specific instance of the tool.

Click the Validate button in the Run group to validate the model.

Click the Run button in the Run group.

For more details, see Open ModelBuilder, Add and connect data and tools, and modify elements, and Run a model.

Run a tool in the Python window

To run a tool in Python, complete the following steps:

On the Analysis ribbon, in the Geoprocessing group, click the drop-down menu under the Python button and click the Python window button.

Type arcpy at the Python prompt in the window.

Start typing the name of the tool. A set of matching tool names are listed in a drop-down menu.

Click the tool name. The tool is added to the code in the Python prompt.

Enter valid parameter values. The syntax for parameters appears when you click in the Python prompt. The Python prompt will contain something similar to the following: arcpy.analysis.Buffer("c:/data/Portland.gdb/streets", "c:/data/Portland.gdb/steets_buffer", "500 METERS").

Press Enter to run the tool.

For more details, see Using tools in Python.