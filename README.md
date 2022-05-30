##############################################################################################
# RFM ile Müşteri Segmentasyonu
###############################################################################################

##############################################################################################
# 1.İş Problemi
###############################################################################################

#Bir e-ticaret şirketi müşterilerini segmentlere ayırıp bu segmentlere göre pazarlama stratejileri belirlemek istiyor.

#Değişkenler

#İnvoiceNo : Fatura numarası : Her işleme yani faturaya eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode : Ürün kodu. Her bir ürün için eşsiz numara.
# Description : Ürün ismi
# Quantity : Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# UnitPrice :  Ürün fiyatı (Sterlin üzerinden)
# InvoiceDate :  Fatura tarihi ve zamanı
# CustomerId : Eşsiz Müşteri numarası
# Country : Ülke ismi : Müşterinin yaşadığı ülke
