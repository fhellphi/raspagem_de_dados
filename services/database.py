from supabase import create_client, Client

class Supabase:
    def __init__(self, supabase_url, supabase_key):
        
        if not supabase_url:
            raise Exception(
                "Supabase URL não configurada."
            )

        if not supabase_key:
            raise Exception(
                "Supabase KEY não configurada."
            )
        self.supabase_url = supabase_url,
        self.supabase_key = supabase_key
        self.supabase_client : Client = create_client(
            supabase_url,
            supabase_key
        )
    
    
    def select(self,schema, table, where=None):
        query = (
            self.supabase_client
            .schema(schema)
            .table(table)
            .select('*')
        )
        
        if where == 0:
            query.execute()
        
        else:
            for coluna, valor in where.items():
                query = query.eq(coluna, valor )\
                
            response = query.execute()
            
            return response.data

    def  insert(self, schema, table, data,):
        response = (
            self.supabase_client
            .schema(schema)
            .table(table)
            .insert(data)
            .execute()
        ) 
        
        return response.data
       
    def delete(self, table,  where):
        pass
    def update(self, table, where):
        pass