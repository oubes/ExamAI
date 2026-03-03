from langgraph.graph import StateGraph, START, END
from app.core.state_graph.agent_types import AgentState
from app.core.state_graph.nodes import *

class WorkflowGraph:
    def __init__(self):
        self.graph = StateGraph(AgentState)
        self._add_nodes()
        self._add_edges()

    def _add_nodes(self):
        self.graph.add_node("Student Submission", student_submission)
        self.graph.add_node("Data Router", data_router)
        self.graph.add_node("OCR Pipeline", ocr_pipeline)
        self.graph.add_node("Token Quality Check", token_quality_check)
        self.graph.add_node("Security & Guardrails", security_guardrails)
        self.graph.add_node("Grading Engine", grading_engine_node)
        self.graph.add_node("Feedback Generator", feedback_generator_node)

    def _add_edges(self):
        g = self.graph

        g.add_edge(START, "Student Submission")
        g.add_edge("Student Submission", "Data Router")
        g.add_edge("Data Router", "OCR Pipeline")
        g.add_edge("OCR Pipeline", "Token Quality Check")
        g.add_edge("Token Quality Check", "Security & Guardrails")
        g.add_edge("Security & Guardrails", "Grading Engine")
        g.add_edge("Grading Engine", "Feedback Generator")
        g.add_edge("Feedback Generator", END)

    def compile(self):
        return self.graph.compile()


workflow = WorkflowGraph()
orchestrator = workflow.compile()
