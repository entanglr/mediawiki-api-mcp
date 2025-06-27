# wiki_meta_siteinfo

Get overall site information from MediaWiki.

This tool corresponds to the MediaWiki API:Siteinfo endpoint and allows retrieving comprehensive information about the MediaWiki installation.

## Parameters

### siprop (list[str], optional)
Which information to get. Default: ["general"]

Available options:
- **general**: Overall system information
- **namespaces**: List of registered namespaces and their canonical names
- **namespacealiases**: List of registered namespace aliases
- **specialpagealiases**: List of special page aliases
- **magicwords**: List of magic words and their aliases
- **interwikimap**: Returns interwiki map (optionally filtered, optionally localised)
- **dbrepllag**: Returns database server with the highest replication lag
- **statistics**: Returns site statistics
- **usergroups**: Returns user groups and the associated permissions
- **autocreatetempuser**: Returns configuration for automatic creation of temporary user accounts
- **clientlibraries**: Returns client-side libraries installed on the wiki
- **libraries**: Returns libraries installed on the wiki
- **extensions**: Returns extensions installed on the wiki
- **fileextensions**: Returns list of file extensions allowed to be uploaded
- **rightsinfo**: Returns wiki rights (license) information if available
- **restrictions**: Returns information on available restriction (protection) types
- **languages**: Returns a list of languages MediaWiki supports
- **languagevariants**: Returns a list of language codes for which LanguageConverter is enabled
- **skins**: Returns a list of all enabled skins
- **extensiontags**: Returns a list of parser extension tags
- **functionhooks**: Returns a list of parser function hooks
- **showhooks**: Returns a list of all subscribed hooks
- **variables**: Returns a list of variable IDs
- **protocols**: Returns a list of protocols that are allowed in external links
- **defaultoptions**: Returns the default values for user preferences
- **uploaddialog**: Returns the upload dialog configuration
- **autopromote**: Returns the automatic promotion configuration
- **autopromoteonce**: Returns the automatic promotion configuration that are only done once
- **copyuploaddomains**: Returns the list of allowed copy upload domains

### sifilteriw (str, optional)
Return only local or only nonlocal entries of the interwiki map.
- **"local"**: Return only local interwiki entries
- **"!local"**: Return only non-local interwiki entries

### sishowalldb (bool, optional)
List all database servers, not just the one lagging the most. Default: false

### sinumberingroup (bool, optional)
Lists the number of users in user groups. Default: false

### siinlanguagecode (str, optional)
Language code for localised language names (best effort) and skin names.

## Examples

### Get general site information
```
siprop: ["general"]
```

### Get namespaces and statistics
```
siprop: ["namespaces", "statistics"]
```

### Get all installed extensions and libraries
```
siprop: ["extensions", "libraries", "clientlibraries"]
```

### Get user groups with member counts
```
siprop: ["usergroups"]
sinumberingroup: true
```

### Get local interwiki entries in German
```
siprop: ["interwikimap"]
sifilteriw: "local"
siinlanguagecode: "de"
```

### Get complete database replication information
```
siprop: ["dbrepllag"]
sishowalldb: true
```

## Response Format

The tool returns formatted text with sections for each type of information requested. The response includes:

- **General Information**: Site name, version, URLs, database info, language settings
- **Namespaces**: List of all namespaces with IDs and names
- **Statistics**: Page counts, user counts, edit counts
- **User Groups**: Available user groups and their permissions
- **Extensions**: Installed extensions and their versions
- **And more** depending on the siprop values requested

## MediaWiki API Reference

This tool implements the MediaWiki API:Siteinfo endpoint:
https://www.mediawiki.org/wiki/Special:MyLanguage/API:Siteinfo

## Error Handling

The tool handles various error conditions:
- Invalid siprop values (filtered out automatically)
- Network connectivity issues
- Authentication problems
- Malformed responses

Errors are returned as descriptive text explaining what went wrong.
