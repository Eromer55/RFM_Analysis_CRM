import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows, None)
#Aşağıdaki kod çıktılarda ki sayısal değerlerin kaç decimal gözükmesini ayarlar
pd.set_option('display.float_format', lambda x : '%.3f' % x)

##############################################################################################
# 1.Veriyi Anlama
###############################################################################################

df_ = pd.read_excel('online_retail_II.xlsx', sheet_name="Year 2009-2010")
df = df_.copy()
df.head()

df.shape # Satır - Sutün sayısını öğrenmek için kullanıyoruz.
df.info() # veri setimiz hakkında bilgi edinmek için kullanıyoruz.
df.describe().T # sayısal değişkenlerimiz hakkında kısaca bir istatistiksel özet almak için kullanıyoruz.
df.isnull().sum()

#Eşsiz Ürün Sayısı Nedir ?
df['Description'].nunique()
df['Description'].value_counts().head()

# En çok satılan ürün hangisi ? Bunun çözümü için description bazında quantity leri toplayalım
df.groupby('Description').agg({'Quantity': 'sum'}).head()
df.groupby('Description').agg({'Quantity': 'sum'}).sort_values("Quantity", ascending=False).head()

# Toplam kaç tane eşsiz fatura kesilmiş
df['Invoice'].nunique()

# Fatura Başına toplam ne kadar tutar oluyor ?
df['Total_Price'] = df['Quantity'] * df['Price']
df.groupby('Invoice').agg({'Total_Price': 'sum'}).head()

##############################################################################################
# 2.Veriyi Hazırlama
###############################################################################################

df.isnull().sum()
df.dropna(inplace=True)
df.shape

# İade edilen faturaları çıkartalım
df = df[~df['Invoice'].str.contains("C", na=False)]

##############################################################################################
# 3. RFM Metriklerinin Hesaplanması
###############################################################################################

# RFM ; Recency, Frequency, Monetary

# Son işlem gününe bakalım ve ondan sonraki bir güne today diyelim.
df['InvoiceDate'].max()

today_date = dt.datetime(2010, 12, 11)
type(today_date)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                    'Invoice': lambda num: num.nunique(),
                                    'Total_Price': lambda Total_Price: Total_Price.sum()})

rfm.columns = ['recency','frequency','monetary']
rfm.describe().T

#decribe sonrası gördük ki monetary min değeri 0 idi. 0 lardan kurtulmamız gerekiyor.
rfm = rfm[rfm['monetary'] > 0]
rfm.describe().T

##############################################################################################
# 4. RFM Skorlarının Hesaplanması
###############################################################################################

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

##############################################################################################
# 5. RFM Segmentlerinin Oluşturulması ve Analiz Edilmesi
###############################################################################################

# regex : Bu bir yaklaşım. Frequency 5 olan ve recency si 5 olana campion yaz.
seg_map = {r'[1-2][1-2]': 'hibernating',
           r'[1-2][3-4]': 'at_Risk',
           r'[1-2]5': 'cant_loose',
           r'3[1-2]': 'about_to_sleep',
           r'33': 'need_attention',
           r'[3-4][4-5]': 'loyal_customers',
           r'41': 'promising',
           r'51': 'new_customers',
           r'[4-5][2-3]': 'potential_loyalist',
           r'5[4-5]': 'champions'
}

rfm['segment']= rfm['RF_SCORE'].replace(seg_map, regex=True)

rfm[['segment', 'recency', 'frequency', 'monetary']].groupby('segment').agg(['mean', 'count'])

new_df = pd.DataFrame()
new_df["new_customers"] = rfm[rfm["segment"] == "new_customers"].index
new_df["new_customers"] = new_df["new_customers"].astype(int)
new_df.to_csv("new_customers.csv")

##############################################################################################
# 6. Tüm Sürecin Fonksiyonlaştırılması
###############################################################################################

def create_rfm(dataframe, csv=False):

    #Veriyi hazırlama
    dataframe["Total_Price"] = dataframe['Quantity'] * dataframe['Price']
    dataframe.dropna(inplace=True)
    dataframe = dataframe[~dataframe['Invoice'].str.contains("C", na=False)]

    #RFM Metriklerinin Hesaplanması
    today_date = dt.datetime(2010, 12, 11)
    rfm = dataframe.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                         'Invoice': lambda num: num.nunique(),
                                         'Total_Price': lambda Total_Price: Total_Price.sum()})
    rfm.columns = ['recency', 'frequency', 'monetary']
    rfm = rfm[rfm['monetary'] > 0]

    #RFM Skorlarının Hesaplanması
    rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

    #cltv_df skorlarının kategroik değere dönüştürülmesi ve df'e eklenmesi
    rfm["RF_SCORE"] = (rfm['recency_score'].astype(str) + rfm['frequency_score'].astype(str))

    #Segmentlerin İsimlendirilmesi
    seg_map = {r'[1-2][1-2]': 'hibernating',
               r'[1-2][3-4]': 'at_Risk',
               r'[1-2]5': 'cant_loose',
               r'3[1-2]': 'about_to_sleep',
               r'33': 'need_attention',
               r'[3-4][4-5]': 'loyal_customers',
               r'41': 'promising',
               r'51': 'new_customers',
               r'[4-5][2-3]': 'potential_loyalist',
               r'5[4-5]': 'champions'
               }

    rfm['segment'] = rfm['RF_SCORE'].replace(seg_map, regex=True)
    rfm = rfm[['segment', 'recency', 'frequency', 'monetary']]
    rfm.index = rfm.index.astype(int)

    if csv:
        rfm.to_csv('rfm.csv')

    return rfm


df = df_.copy()
rfm_new = create_rfm(df)
rfm_new.head()
