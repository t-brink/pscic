import pyparsing

def evaluate(tree):
    if not isinstance(tree, pyparsing.ParseResults):
        return tree
    fn = tree[0]
    ops = []
    for i in tree[1:]:
        if isinstance(i, pyparsing.ParseResults):
            i_eval = evaluate(i)
        else:
            i_eval = i
        ops.append(i_eval)
    retval = fn(*ops)
    return retval

