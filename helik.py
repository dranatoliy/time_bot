import  tinkoffpy as tf


def zapros_popolnenia(date_from, date_to, number):
    query = f'''
    SELECT  client_id,
    account_number,
    payment_dttm + interval '3 hours' as payment_dtt, 
    payment_amt as summa,  	
    src_system_code,
    src_system_no, 
    src_system_desc,
    proc_status
    from  prod_usermart.ops_fin_request
    WHERE payment_dttm BETWEEN '{date_from}' and '{date_to}' and (client_id = '0000{number}' or client_id = '00000{number[1:]}')
    '''
    print(query)
    df = tf.click_to_df(query, clickhouse_service="dwh")
    return df


def zapros_popolnenia_date(date_from,summa):
    query = f'''
    SELECT  client_id,
    account_number,
    payment_dttm + interval '3 hours' as payment_dtt, 
    payment_amt as summa,  	
    src_system_code,
    src_system_no, 
    src_system_desc,
    proc_status
    from  prod_usermart.ops_fin_request
    WHERE payment_dttm BETWEEN '{date_from}' and '{date_from}' + INTERVAL '1 days' and payment_amt = {summa}
    limit 1000
    '''
    print(query)
    df = tf.click_to_df(query, clickhouse_service="dwh")
    return df

