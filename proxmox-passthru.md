# PCIe passthru

```bash
cat /proc/cmdline; for d in /sys/kernel/iommu_groups/*/devices/*; do n=${d#*/iommu_groups/*}; n=${n%%/*}; printf 'IOMMU group %s ' "$n"; lspci -nns "${d##*/}"; done
```

https://forum.proxmox.com/threads/prevent-a-sata-controller-to-be-loaded-by-ahci.136983/post-608610

```bash
update-initramfs -u -k all
```