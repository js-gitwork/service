from django.http import JsonResponse
import json

def test_report(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("\n=== DEBUG: MODTAGET I TEST_VIEW ===")
        print("VPID:", data.get('VPID'))
        print("description:", data.get('description'))
        print("sprog:", data.get('sprog', 'IKKE MODTAGET!'))  # Kritisk linje
        return JsonResponse({'status': 'success', 'data': data})
