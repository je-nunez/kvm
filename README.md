# kvm

Notes:

       systool -vm kvm

Stats (libvirt):

       virsh dommemstat "${my_dom_name}"
        
       virsh domstats   "${my_dom_name}"
        
       virsh cpu-stats  "${my_dom_name}"
        
       virsh event      "${my_dom_name}" --timestamp

       dmesg            # e.g., dmesg | fgrep -i kvm

Migrate/Save (libvirt):

       virsh migrate     "${my_dom_name}"  "$destination"
        
       virsh managedsave "${my_dom_name}"

