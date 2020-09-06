# MathReader: API for handwritten mathematical expressions recognition

__GitHub:__ [mathreader](https://github.com/carolreis/mathreader)

## About:

- __Accepted symbols__: 
    - {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "m", "n", "x", "y", "z", "+", "-", "*", "sqrt", "=", "neq"}

- __Internal modules__:
    - Image preprocessing
    - Image posprocessing
    - Symbol recognition
    - Structural analysis
    - Lexical analysis
    - Sintatic analysis
    - Grammar correction

## Usage:

Example in: [main.py](main.py)

```
from api import *

hme_recognizer = HME_Recognizer()

image = ['images/numbers/teste10.png']

try:
    hme_recognizer.load_image(image)
    expression, img = hme_recognizer.recognize()
    print("Latex: ", expression)
except Exception as e:
    print('Exception: ', e)
```
---------------------------

### Configuration

Configuration file is in [docs/config.json](docs/config.json)

```
{
    "application": {
        "debug_mode": "active",
        "debug_mode_image": "active"
    }
}
```

- debug_mode: active
activate debug messages in terminal
- debug_mode_image: active
show the images during the execution for debugging

### HME_Recognizer
All attributes and methods avaiable in __HME_Recognizer__ class at [api.py](api.py)

#### Attributes:
    - image
    - parsed_expression
    - processed_image
    - predictions
    - configurations
    - expression_after_recognition
    - expression_after_parser
    - expression_after_grammar
    - parser_tree
    - parser_list
    - lex_errors
    - yacc_errors
    - pure_lex_errors
    - pure_yacc_errors

#### Methods

- load_image(image)
    - First method you should call.
    - It loads the image containing the expression.
    - __Input:__ image.
    - __Returns:__ None.

- recognize()
    - Second method you should call.
    - It makes the recognition of the image containing the expression.
    - __Input:__ None.
    - __Returns:__
        - expression: latex of the expression
        - image: image after processing

- reset()
    - Reset all attributes from HME_Recognizer()
    - __Input:__ None.
    - __Returns:__ None

- get_predictions()
    - Get all predictions from neural network
    - __Input:__ None.
    - __Returns:__ List of predictions.

- get_expression_after_parser()
    - Get expression after going to parser module
    - __Input:__ None.
    - __Returns:__ (list) expression

- get_expression_after_grammar()
    - Get expression after grammar check and correction
    - __Input:__ None.
    - __Returns:__ (str) expression

- get_expression_after_recognition()
    - Get expression after recognition module
    - __Input:__ None.
    - __Returns:__ (dict) expression

- get_configurations()
    - Get configuration from configuration file [docs/config.json](docs/config.json)
    - __Input:__ None.
    - __Returns:__ configurations

- get_lex_errors()
    - Get lex errors with a structure used by the grammar check
- get_yacc_errors()
    - Get yacc errors with a structure used by the grammar check
- get_pure_lex_errors()
    - Get 'pure' lex errors coming from PLY (Python Lex Yacc)
- get_pure_yacc_errors()
    - Get 'pure' yacc errors coming from PLY (Python Lex Yacc)
