## Requirements
- Python3
- prettytable (only if you need tables)

## Usage
`huffman.py [-h] [-e] [-d DATA] [-t] [input]`<br>

Arguments:
- `input`: The input string. Can be ommitted to use stdin
- `-e`: Show the Huffman encoded input
- `-t`: Show the generated Huffman Tree
- `-d (OPTION=PARAMS,)*(OPTION=PARAMS)`: Show generated data in formated table:
  - `[c|columns]=PARAM+`: Show columns in the parameters
    - `p(\{FORMAT\})?`: Char probabilites. Optionaly a format string can be added
    - `w`: Huffman codewords
    - `l`: Huffman codeword lengths
  - `[s|sortby]=[p|w|l]`: Sort table by a column
  - `[r|reverse]`: Reverse sort order
  
 ## Examples
 - Show all data, sorted by codewords in reverse order:<br>
   __`python huffman.py -d c=pwl,s=w,r "huffman"`__
   ```
    +-------+-----+-----------+---------+
    | Chars |  P  | Codewords | Lengths |
    +-------+-----+-----------+---------+
    |   a   | 1/7 |    111    |    3    |
    |   h   | 1/7 |    110    |    3    |
    |   m   | 1/7 |    011    |    3    |
    |   n   | 1/7 |    010    |    3    |
    |   u   | 1/7 |     10    |    2    |
    |   f   | 2/7 |     00    |    2    |
    +-------+-----+-----------+---------+
   ````
- Input from stdin:<br>
  __`echo huffman | python huffman.py`__<br>
  `110100000011111010`
