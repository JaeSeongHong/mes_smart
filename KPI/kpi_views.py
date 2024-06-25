

from api.models import KpiLog
from datetime import datetime

def kpi_log(enterprise, user_name, module, crud, error):
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        # module_name = str(module._meta)

        KpiLog.objects.create(
            enterprise=enterprise,  # 업체
            created_by=user_name,  # 로그인 유저
            kpiDate=today,  # 처리일자
            module=module,  # 사용모듈 (모델명)
            crud=crud,  # CRUD
            error=error,  # 트랜잭션 수행 row 수
        )

    except:
        print('kpi_log error %r' % module)