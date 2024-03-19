# studio-custom-names

This Tool allows you to use custom part names in Stud.io, in case you struggle with bricklink's names.
This is made for windows, and won't work with MacOS.

## Usage

1. Adjust the renaming rules in the ``rules`` directory following [this format](#rules).
2. Run "main.py"
3. If Studio is running, close it.
4. Start Studio and enjoy your custom part names.

## Rules

The rules are stored in the ``rules`` directory. Each file in this directory is a ``.rules`` file.  
Creating different files allows you to group different rules together.  

> [!WARNING]
> The rules are applied in the order they are read from the filesystem.
> This means the files are being read in alphabetical order and the rules in each file are applied in the order they are read from the file (from top to bottom).
> Also, the rules are applied one after another, so the result of the first rule is used as the input for the second rule, and so on.
> To avoid problems with regex-rules, make sure each part is only renamed once and never matches the new name of a part that has already been renamed.
> (Except you know what you are doing)
  
There are two types of rules. In both, empty lines and lines starting with ``#`` are ignored. (Spaces before the ``#`` invalidate the comment.)

### ID Rules

ID-based rulesets are defined in files with the ``.id.rules`` extension.  
In these files, each line contains a rule in the following format:

```plaintext
<id> => <new_name>
```

Where ``<id>`` is the part's ID (on bricklink) and ``<new_name>`` is the name you want to give to the part.

### Regex Rules

Regex-based rulesets are defined in files with the ``.regex.rules`` extension.  
In these files, each line contains a rule in the following format:

```plaintext
<regex> => <new_name>
```

Where ``<regex>`` is a regular expression that matches the part's (bricklink) name and ``<new_name>`` is the name you want to give to the part.
This can be useful to rename multiple parts at once, like renaming all liftarms to beams, using the following rule:

```plaintext
^Technic, Liftarm Thick 1 x (\d+)$ => {0}er Beam
```

In this example, the ``{0}`` placeholder is replaced by the first capture group in the regular expression, which is the length of the liftarm. ``(\d+)`` matches one or more digits, and the ``^`` and ``$`` match the start and end of the name. For more tips for regular expressions, see [this tool](https://regex101.com).
You can use as many capture groups as you want, and they are numbered from 0 to infinity.

## Changing the rules

If you want to change the part names, you can simply edit the rules files in the ``rules`` directory and run the script again.

The rules are always applied ontop of the original part names, so you dont have to change the rules alltogether if you want to change the part names again.

## Reverting the changes

To revert the changes, simply delete the ``StudioPartsDefinition2.txt`` file in the ``data`` folder in the Studio installation directory (for Windows usually ``C:\Program Files\Studio 2.0\data``).
Then, move/rename the ``StudioPartsDefinition2.txt.original`` file to ``StudioPartsDefinition2.txt``.

Alternatively, you can run delete all the rules files in the ``rules`` directory and run the script again.

## After an Studio update

After an update of Studio, the ``StudioPartsDefinition2.txt`` file may be overwritten. Please open Studio and see if the changed part names are still correct.
If not, you have to delete the ``StudioPartsDefinition2.txt.original`` file and run the script.
