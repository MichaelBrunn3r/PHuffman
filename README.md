## About
This little tool is supposed to help when calculating the Huffman codes of a string by hand.
It expects you to follow this algorithm:
- Count relative probability of all unique Chars in the string and sort them alphabetically.
Making a table for reference might be usefull
- Create a Huffman Tree with this algorithm:
  - The tree is going to be built from the bottom up
  1. Create leave nodes at the bottom for every char, sorted first by probability and then alphabetically
  2. Take the two smallest probabilites, starting from the left, and sum up their probabilites
  3. Add the resulting parent node with the calcualted probability. It should sit right above its children
  - !!! Never reorder any nodes !!! The new parent node should not move right of any other node to its right. If the children nodes are far apart from another, put the parent above the left child
  4. Repeat from step ii until only one node is left
- Now you can calculate the Huffman codes. For every leave/char, traverse the tree from the top. Everytime you go left, add a 1 to the code, if you go right, add a 0.

If you follow this algorithm correctly, your codes will match those generated by this program.
  

## Requirements
- Python3
- [prettytable](https://pypi.org/project/PrettyTable/) (only if you need pretty printed tables)

## Usage
`python huffman.py [-h] {encode,table}`<br>
Arguments:
- `{encode,table}`: The subcommand to run

#### Subcommand Encode
Encodes an input string to Binary using the Huffman Codes generated from it.

Usage: `python huffman.py encode [-h] [string] [-x]`<br>
Arguments:
- `string`: The input string to encode. Omit to use stdin instead.
- `-x`: Set this flag so that the 

#### Subcommand Table
Prints a table of the data resulting from generating the Huffman Codes from the input string.
Usefull as a reference for when you create Huffman Codes by hand.

Usage: `python huffman.py table [-h] [string] [-c] [-s] [-r] [-p]`<br>
Arguments:
- `string`: The input string to generate the Huffman Codes from. Omit to use stdin instead.
- `-c`: A list of the columns included in the output table, in that order.
  - Structure: `(<column>{<options>})+`
  - `<options>`: A python dictionary with indivudual settings for the column. <br>
    Possible options depend on column type.
  - `<column>`: The column abbreviation
    - `c`: The Huffman Codewords
      - option `hex`: Prints the codeword as a hex string 
    - `l`: The length of the Huffman Codewords
    - `o`: The absolute occurences of each char
    - `p`: The probability of each char
      - option `f`: The format for the decimal number
- `-s`: Sort the table by this column
- `-r`: Sort in reverse
- `-p`: Pretty print the table using prettytable

## Examples
- Encode string in binary:<br>
  `python huffman.py encode "huffman"`<br>
  `110100000011111010`
- Encode string in hex:<br>
  `python huffman.py encode "huffman" -x`<br>
  `340fa`
- Print table with probabilites and codewords:<br>
  `python huffman.py table "huffman" -c pc`
  ```
  a;1/7;111
  f;2/7;00
  h;1/7;110
  m;1/7;011
  n;1/7;010
  u;1/7;10
  ```
- Print pretty printed table, columns probability and codewords:<br>
  `python huffman.py table "huffman" -c pc -p`
  ```
  +-------+-----+--------------+
  | Chars |  P  | Huffman Code |
  +-------+-----+--------------+
  |   a   | 1/7 |     111      |
  |   f   | 2/7 |      00      |
  |   h   | 1/7 |     110      |
  |   m   | 1/7 |     011      |
  |   n   | 1/7 |     010      |
  |   u   | 1/7 |      10      |
  +-------+-----+--------------+
  ```
- Print pretty printed table, columns 'pc', formated probabilities, sorted reverse by probabilites:<br>
  `python .\huffman.py table "huffman" -c "p{'f':':.4f'}c" -p -s p -r`
  ```
  +-------+--------+--------------+
  | Chars |   P    | Huffman Code |
  +-------+--------+--------------+
  |   f   | 0.2857 |      00      |
  |   u   | 0.1429 |      10      |
  |   n   | 0.1429 |     010      |
  |   m   | 0.1429 |     011      |
  |   h   | 0.1429 |     110      |
  |   a   | 0.1429 |     111      |
  +-------+--------+--------------+
  ```
- Input from stdin:<br>
  `echo "huffman" | python .\huffman.py encode`<br>
  `110100000011111010`
  
