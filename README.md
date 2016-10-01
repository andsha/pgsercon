# pgsercon
server configuration tool for postgresql data base

Requires Python3 and PyQt4

The main window displays (on the left) current configuration file, list of templates, and a list of Postgres versions with default parameters; (in the middle) list of parameter groups; (on the right) a table with parameters from current group, its default value, and short description.

Program provides a list of default parameters for Postgres version from 9.2 to 9.6. After choosing particular version a list of parameter groups shall appear in the middle panel. Clicking on the group name displays a table of parameters from current group in the right window. In addition it also displays parameter type, default version, and short description. The check box to the left from parameter name indicated if current parameter is being used in configuration file. Also, “More…” link to the right from parameter description leads to the Postgres web page with complete parameter description.

In the left part of the window there is table displaying parameters for current configuration file. Table displays parameter name and parameter value. Parameters can be added to the table by either loading existing configuration file (e.g. postgresql.conf) or enabling use of the parameter in the default values table. By double-clicking on the parameter name a corresponding entry from the default table will be shown. By double-clicking on the value field the editing of the field will be enabled. White background of the parameter entry indicates the value of the parameter equals to the default. Green - newly added parameter. Blue - parameter whose value does not equal to default. Red - parameter which does not exist in the default table.

Current configuration table can be saved into postgres configuration file.

Program also allows insert a set of pre-defined parameters (templates).