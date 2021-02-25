# FTP metrics
    collect data of timeout counts and overkill & leak rate to prometheus by golang
---

Parse FTP human rejudged data, **such as daily quantity of Overkill & Leak and all filenames under the folder "Overkill & Leak"** into prometheus metrics to reduce daily report loading.

## FTP

FTP has the following path format:

/dip-prewave-saiap/**LINE**/**DATE**/**LABEL**/filename.png

> LINE: DA2, DA4 </br>
LABEL: OK, NG, Overkill, Leak

## Metrics

**with label: line, date**
</br>true OK/NG contain false OK/NG
> true NG: metrics_true_ng</br>
> true OK: metrics_true_ok</br>
> false NG (Overkill): metrics_false_ng</br>
> false OK (Leak): metrics_false_ok</br>

### query to apply in dashboard
- total quantity: tO + tN
- accuracy: (tO -fO + tN - fN) / (tO + tN)
- overkill rate: fN / tN
- Leak rate: fO / tO
