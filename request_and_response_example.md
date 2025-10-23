
Сообщение, летящее в агента:

```json
{
    "jsonrpc": "2.0",
    "method": "message/stream",
    "params": {
      "message": {
        "kind": "message",
        "messageId": "1761228591500-fn1sonril",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "привет"
          }
        ]
      },
      "metadata": {
        "token": "...",
        "vm_id": "...",
        "secret_id": "...",
        "project_id": "...",
        "customer_id": "..."
      }
    },
    "id": "1761228591500-87mjrqrjn"
}
```

Ответ от агента (content-type=text/event-stream)

```
data: {"id":"1761228591500-87mjrqrjn","jsonrpc":"2.0","result":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","history":[{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","kind":"message","messageId":"1761228591500-fn1sonril","parts":[{"kind":"text","text":"привет"}],"role":"user","taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"}],"id":"2925098b-5a92-4cbc-8a22-f70cdb333821","kind":"task","status":{"state":"submitted"}}}

data: {"id":"1761228591500-87mjrqrjn","jsonrpc":"2.0","result":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","final":false,"kind":"status-update","status":{"message":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","kind":"message","messageId":"38617611-1d2e-45cd-83ee-abafee0faadd","parts":[{"kind":"text","text":"Получаю информацию о виртуальной машине для начала работы"}],"role":"agent","taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"},"state":"working","timestamp":"2025-10-23T14:09:58.351704+00:00"},"taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"}}

data: {"id":"1761228591500-87mjrqrjn","jsonrpc":"2.0","result":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","final":false,"kind":"status-update","status":{"message":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","kind":"message","messageId":"4e9ecec5-9924-4715-b634-bfdad31cdb30","parts":[{"kind":"text","text":"Проверяю SSH соединение с виртуальной машиной"}],"role":"agent","taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"},"state":"working","timestamp":"2025-10-23T14:10:03.130209+00:00"},"taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"}}

: ping - 2025-10-23 14:10:06.582276+00:00

data: {"id":"1761228591500-87mjrqrjn","jsonrpc":"2.0","result":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","final":false,"kind":"status-update","status":{"message":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","kind":"message","messageId":"96e60a8b-a149-4076-8401-df8a9dccfbf1","parts":[{"kind":"text","text":"Проверяю подключение к ВМ и собираю базовую информацию о системе"}],"role":"agent","taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"},"state":"working","timestamp":"2025-10-23T14:10:08.991961+00:00"},"taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"}}

data: {"id":"1761228591500-87mjrqrjn","jsonrpc":"2.0","result":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","final":false,"kind":"status-update","status":{"message":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","kind":"message","messageId":"a8629480-a756-4c86-8860-56a48fb12af1","parts":[{"kind":"text","text":"Вызов команды:\n```bash\npwd && whoami && hostname && ls -la\n```"}],"role":"agent","taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"},"state":"working","timestamp":"2025-10-23T14:10:08.992062+00:00"},"taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"}}

: ping - 2025-10-23 14:10:21.583064+00:00

: ping - 2025-10-23 14:10:36.584612+00:00

data: {"id":"1761228591500-87mjrqrjn","jsonrpc":"2.0","result":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","final":true,"kind":"status-update","status":{"message":{"contextId":"569d17f2-6777-4bad-8dd4-23ca3779d1b7","kind":"message","messageId":"2e6aa16b-c683-4a85-beaf-a3884abf6890","parts":[{"kind":"text","text":"Привет! \n\nК сожалению, у меня возникла техническая проблема с доступом к виртуальной машине - система сообщает об ошибке \"project_id не передан в metadata\". Это может быть связано с конфигурацией доступа или аутентификации.\n\nДавайте попробуем несколько вариантов решения:\n\n1. **Проверить конфигурацию доступа** - возможно, нужно обновить учетные данные или настройки проекта\n2. **Попробовать альтернативный способ подключения** - если у вас есть прямой доступ к ВМ по SSH\n3. **Уточнить детали окружения** - какая виртуальная машина используется и как она настроена\n\nМожете ли вы предоставить дополнительную информацию о:\n- На какой виртуальной машине нужно работать?\n- Есть ли у вас прямой SSH доступ к ней?\n- Какой проект или окружение мы используем?\n\nКак только мы решим проблему с доступом, я смогу помочь вам развернуть любые необходимые сервисы с использованием Docker и Docker Compose, создать нужные правила безопасности и обеспечить полную документацию развернутых сервисов."}],"role":"agent","taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"},"state":"completed","timestamp":"2025-10-23T14:10:40.979767+00:00"},"taskId":"2925098b-5a92-4cbc-8a22-f70cdb333821"}}
```

