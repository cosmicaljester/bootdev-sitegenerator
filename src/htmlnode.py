class HTMLNode:
    def __init__(self, tag: str|None = None, value: str|None = None, children: list['HTMLNode']|None = None, props: dict|None = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()
    
    def props_to_html(self):
        if self.props == None or len(self.props) < 1:
            return ''
        prop = ''
        for elem in self.props:
            prop += f' {elem}=\"{self.props[elem]}\"'
        return prop
    
    def __repr__(self):
        return 'tag: {}\nvalue: {}\nchildren: {}\nprops: {}'.format(self.tag,self.value,self.children,self.props)

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props = None):
        super().__init__(tag,None,children,props)
    
    def to_html(self):
        if self.tag is None:
            raise ValueError('Parent missing tag')
        if self.children is None:
            raise ValueError('Parent {} missing children'.format(self.tag))
        hell = '<{}{}>'.format(self.tag,self.props_to_html())
        for child in self.children:
            hell += child.to_html()
        hell += '</{}>'.format(self.tag)
        return hell

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props = None):
        super().__init__(tag,value,None,props)
    
    def to_html(self):
        if self.value is None:
            raise ValueError('No value on tag {}'.format(self.tag))
        if self.tag is None:
            return self.value
        return "<{}{}>{}</{}>".format(self.tag,self.props_to_html(),self.value,self.tag)
    
    def __repr__(self):
        return 'tag: {}\nvalue: {}\nprops: {}'.format(self.tag,self.value,self.props)
