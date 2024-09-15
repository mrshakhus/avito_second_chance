class TendersService:
    @staticmethod
    async def get_tenders(
        limit: int,
        offset: int,
        service_type: list[str]
    ) -> list[dict]:
        pass