#! /usr/bin/bash



if [ ! -e /dev/md* ]; then
  
          # Занулить суперблоки на дисках

                mdadm --zero-superblock --force /dev/sd{b,c,d,e,f,g,h} > /dev/null 2>&1

        # Удаляем старые метаданные и подпись на дисках

                wipefs --all --force /dev/sd{b,c,d,e,f,g,h} > /dev/null 2>&1

        # создание рейда 5-го уровня

                mdadm --create --verbose /dev/md0 -l 5 -n 5 /dev/sd{b,c,d,e,f} > /dev/null 2>&1


        # Создание файла mdadm.conf

                if [ ! -d "/etc/mdadm" ]; then

                        mkdir /etc/mdadm
                        echo "DEVICE partitions" > /etc/mdadm/mdadm.conf  
                        mdadm --detail --scan --verbose | awk '/ARRAY/ {print}' >> /etc/mdadm/mdadm.conf

                fi

        # Создаем раздел GPT на RAID

                parted -s /dev/md0 mklabel gpt
        # Разбиваем на разделы  
                parted /dev/md0 mkpart primary ext4 0% 20%
                parted /dev/md0 mkpart primary ext4 20% 40%
                parted /dev/md0 mkpart primary ext4 40% 60%
                parted /dev/md0 mkpart primary ext4 60% 80%
                parted /dev/md0 mkpart primary ext4 80% 100%

        # Создание файловой системы на разделах
                for i in $(seq 1 5); do 
                
                        sudo mkfs.ext4 /dev/md0p$i
                
                done

                
                
else
        echo "Рейд существует"
        echo $(ls /dev/md*)
        exit 1
        
fi
  
