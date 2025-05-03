from lark import Transformer, v_args

@v_args(inline=True) 
class MyTransformer(Transformer):
