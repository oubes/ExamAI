from app.core.state_graph.graph_manager import *

result = app.invoke(
    {
        "msg": "Hello World"
    }
)
print(result)