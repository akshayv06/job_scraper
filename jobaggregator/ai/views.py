from rest_framework.decorators import api_view
from rest_framework.response import Response

from .agent import run_agent

@api_view(['POST'])
def agent_view(request):

    query = request.data.get("query")

    if not query:
        return Response({"error": "Query required"}, status=400)

    result = run_agent(query)

    return Response(result)