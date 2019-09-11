# iTunesToM3ULibrary

Converts iTunes library playlsits/folders/lately added into M3U playlists. 

## Use

```
python3 main.py /path/to/config.json
```

## Configuration file
JSON file should consist of a dictionary containing settings. 
```json
{
  "setting1": "value1",
  "setting2": "value2"
}
```

For an overview about all settings refer to [settings.py](https://github.com/okehargens/iTunesToM3ULibrary/blob/master/src/configuration.py). 

Example settings files `configs/settings_*.py`. For example: 
[settings_base.json](https://github.com/okehargens/iTunesToM3ULibrary/blob/master/configs/settings_base.json) &
[settings_X3.json](https://github.com/okehargens/iTunesToM3ULibrary/blob/master/configs/settings_X3.json)

## Disclaimer
Use on your own responsibility. I take no responsibility for data loss, that may be caused by misconfiguration or bugs.
