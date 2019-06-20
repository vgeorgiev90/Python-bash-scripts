#!/bin/bash

branch="${1}"
number="${2}"

case $branch in
        'master')
                export TAG="master"
                docker build --no-cache -t registry.gitlab.com/titikpintar/backend-user-ms:$TAG-$number /var/lib/jenkins/workspace/backend-laravel
                docker push registry.gitlab.com/titikpintar/backend-user-ms:$TAG-$number
                sed "s/_APP_NAME_/$TAG/g; s/_VERSION_/$TAG-$number/g" /var/lib/jenkins/deployments/template.yml > /var/lib/jenkins/deployments/deploy-$TAG-$number.yml
                export NAME=backend-$TAG
                kubectl delete deploy $NAME -n dev || true
                kubectl delete ingress $NAME -n dev || true
                kubectl delete svc $NAME -n dev || true
                sleep 20
                kubectl create -f /var/lib/jenkins/deployments/deploy-$TAG-$number.yml
                sleep 20
                POD=$(kubectl get pods -n dev | grep $NAME | awk '{print $1}')
                kubectl -n dev patch ingress/backend-master --patch '{"spec": { "rules" : [{"host": "app.titikpintar.id"}]}}'
                kubectl -n dev exec -it $POD -- sed -i 's/master.dev.titikpintar.id/app.titikpintar.id/' /etc/nginx/conf.d/website.conf
                kubectl -n dev exec -it $POD -- nginx -s reload
                kubectl -n dev exec -it $POD -- /usr/share/nginx/html/vendor/bin/phpunit > /var/lib/jenkins/reports/$POD.report
                cat /var/lib/jenkins/reports/$POD.report | grep -i ok
                if [ $? -ne 0 ];then
                kubectl delete deploy $NAME -n dev || true
                kubectl delete ingress $NAME -n dev || true
                kubectl delete svc $NAME -n dev || true
                fi
                ;;
        'dev')
                export TAG="dev"
                docker build --no-cache -t registry.gitlab.com/titikpintar/backend-user-ms:$TAG-$number /var/lib/jenkins/workspace/backend-laravel
                docker push registry.gitlab.com/titikpintar/backend-user-ms:$TAG-$number
                sed "s/_APP_NAME_/$TAG/g; s/_VERSION_/$TAG-$number/g" /var/lib/jenkins/deployments/template.yml > /var/lib/jenkins/deployments/deploy-$TAG-$number.yml
                export NAME=backend-$TAG
                kubectl delete deploy $NAME -n dev || true
                kubectl delete ingress $NAME -n dev || true
                kubectl delete svc $NAME -n dev || true
                sleep 20
                kubectl create -f /var/lib/jenkins/deployments/deploy-$TAG-$number.yml
                sleep 20
                POD=$(kubectl get pods -n dev | grep $NAME | awk '{print $1}')
                kubectl -n dev exec -it $POD -- /usr/share/nginx/html/vendor/bin/phpunit > /var/lib/jenkins/reports/$POD.report
                cat /var/lib/jenkins/reports/$POD.report | grep -i ok
                if [ $? -ne 0 ];then
                kubectl delete deploy $NAME -n dev || true
                kubectl delete ingress $NAME -n dev || true
                kubectl delete svc $NAME -n dev || true
                fi
                ;;
        *)
                if [[ $branch =~ "feature/" ]];then
                        export TAG=`echo $branch | awk -F"/" '{print $2}'`
                else
                        export TAG=${branch}
                fi
                docker build --no-cache -t registry.gitlab.com/titikpintar/backend-user-ms:$TAG-$number /var/lib/jenkins/workspace/backend-laravel
                docker push registry.gitlab.com/titikpintar/backend-user-ms:$TAG-$number
                sed "s/_APP_NAME_/$TAG/g; s/_VERSION_/$TAG-$number/g" /var/lib/jenkins/deployments/template.yml > /var/lib/jenkins/deployments/deploy-$TAG-$number.yml
                export NAME=backend-$TAG
                kubectl delete deploy $NAME -n dev || true
                kubectl delete ingress $NAME -n dev || true
                kubectl delete svc $NAME -n dev || true
                sleep 20
                kubectl create -f /var/lib/jenkins/deployments/deploy-$TAG-$number.yml
                sleep 20
                POD=$(kubectl get pods -n dev | grep $NAME | awk '{print $1}')
                kubectl -n dev exec -it $POD -- /usr/share/nginx/html/vendor/bin/phpunit > /var/lib/jenkins/reports/$POD.report
                cat /var/lib/jenkins/reports/$POD.report | grep -i ok
                if [ $? -ne 0 ];then
                kubectl delete deploy $NAME -n dev || true
                kubectl delete ingress $NAME -n dev || true
                kubectl delete svc $NAME -n dev || true
                fi
                ;;
esac
echo "PHP UNIT TEST REPORT:"
echo "======================================"
cat /var/lib/jenkins/reports/$POD.report
