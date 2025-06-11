const autocannon = require('autocannon');
const soap = require('strong-soap').soap;
const { promisify } = require('util');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
    duration: 30, // Test duration in seconds
    connections: 100, // Number of concurrent connections
    pipelining: 1, // Number of pipelined requests
    timeout: 10, // Timeout in seconds
    wsdlUrl: 'http://localhost:8000/?wsdl',
    endpoint: 'http://localhost:8000'
};

// Create a SOAP client
async function createSoapClient() {
    const options = {
        endpoint: CONFIG.endpoint,
        forceSoap12Headers: true
    };

    return new Promise((resolve, reject) => {
        soap.createClient(CONFIG.wsdlUrl, options, (err, client) => {
            if (err) {
                reject(err);
                return;
            }
            resolve(client);
        });
    });
}

// Convert SOAP call to Promise
function soapCall(client, method, args) {
    return new Promise((resolve, reject) => {
        client[method](args, (err, result) => {
            if (err) {
                reject(err);
                return;
            }
            resolve(result);
        });
    });
}

// Test scenarios
const testScenarios = [
    {
        name: 'Listar Usuários',
        fn: async (client) => {
            await soapCall(client, 'list_users', {});
        }
    },
    {
        name: 'Listar Todas as Músicas',
        fn: async (client) => {
            await soapCall(client, 'list_all_music', {});
        }
    },
    {
        name: 'Listar Playlists do Usuário',
        fn: async (client) => {
            await soapCall(client, 'list_user_playlists', { user_id: 1 });
        }
    },
    {
        name: 'Listar Músicas da Playlist',
        fn: async (client) => {
            await soapCall(client, 'list_playlist_music', { playlist_id: 1 });
        }
    }
];

// Generate HTML report
function generateHTMLReport(results) {
    const html = `
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Testes de Carga - Serviço SOAP</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .chart-container {
                margin: 20px 0;
                padding: 20px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1, h2 {
                color: #333;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f8f9fa;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Relatório de Testes de Carga - Serviço SOAP</h1>
            <h2>Configuração dos Testes</h2>
            <table>
                <tr>
                    <th>Parâmetro</th>
                    <th>Valor</th>
                </tr>
                <tr>
                    <td>Duração</td>
                    <td>${CONFIG.duration} segundos</td>
                </tr>
                <tr>
                    <td>Conexões Concorrentes</td>
                    <td>${CONFIG.connections}</td>
                </tr>
                <tr>
                    <td>Pipelining</td>
                    <td>${CONFIG.pipelining}</td>
                </tr>
                <tr>
                    <td>Timeout</td>
                    <td>${CONFIG.timeout} segundos</td>
                </tr>
            </table>

            <div class="chart-container">
                <canvas id="requestsChart"></canvas>
            </div>

            <div class="chart-container">
                <canvas id="responseTimeChart"></canvas>
            </div>

            <div class="chart-container">
                <canvas id="successRateChart"></canvas>
            </div>

            <h2>Resultados Detalhados</h2>
            <table>
                <tr>
                    <th>Cenário</th>
                    <th>Total de Requisições</th>
                    <th>Erros</th>
                    <th>Taxa de Sucesso</th>
                    <th>Tempo Médio de Resposta</th>
                    <th>Requisições por Segundo</th>
                </tr>
                ${results.map(r => `
                    <tr>
                        <td>${r.name}</td>
                        <td>${r.requestCount}</td>
                        <td>${r.errorCount}</td>
                        <td>${r.successRate.toFixed(2)}%</td>
                        <td>${r.avgResponseTime.toFixed(2)}ms</td>
                        <td>${r.rps.toFixed(2)}</td>
                    </tr>
                `).join('')}
            </table>
        </div>

        <script>
            const results = ${JSON.stringify(results)};
            
            // Gráfico de Requisições
            new Chart(document.getElementById('requestsChart'), {
                type: 'bar',
                data: {
                    labels: results.map(r => r.name),
                    datasets: [{
                        label: 'Total de Requisições',
                        data: results.map(r => r.requestCount),
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Total de Requisições por Cenário'
                        }
                    }
                }
            });

            // Gráfico de Tempo de Resposta
            new Chart(document.getElementById('responseTimeChart'), {
                type: 'bar',
                data: {
                    labels: results.map(r => r.name),
                    datasets: [{
                        label: 'Tempo Médio de Resposta (ms)',
                        data: results.map(r => r.avgResponseTime),
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Tempo Médio de Resposta por Cenário'
                        }
                    }
                }
            });

            // Gráfico de Taxa de Sucesso
            new Chart(document.getElementById('successRateChart'), {
                type: 'bar',
                data: {
                    labels: results.map(r => r.name),
                    datasets: [{
                        label: 'Taxa de Sucesso (%)',
                        data: results.map(r => r.successRate),
                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Taxa de Sucesso por Cenário'
                        }
                    }
                }
            });
        </script>
    </body>
    </html>
    `;

    fs.writeFileSync(path.join(__dirname, 'relatorio_teste_carga.html'), html);
}

// Run load test for a specific scenario
async function runLoadTest(scenario) {
    console.log(`\n🚀 Executando teste de carga para: ${scenario.name}`);
    
    const client = await createSoapClient();
    let requestCount = 0;
    let errorCount = 0;
    let totalResponseTime = 0;

    const startTime = Date.now();
    const endTime = startTime + (CONFIG.duration * 1000);

    while (Date.now() < endTime) {
        try {
            const requestStart = Date.now();
            await scenario.fn(client);
            const requestEnd = Date.now();
            
            totalResponseTime += (requestEnd - requestStart);
            requestCount++;
        } catch (error) {
            errorCount++;
            console.error(`Erro em ${scenario.name}:`, error.message);
        }
    }

    const duration = (Date.now() - startTime) / 1000;
    const avgResponseTime = totalResponseTime / requestCount;
    const successRate = ((requestCount - errorCount) / requestCount * 100);
    const rps = requestCount / duration;

    console.log(`\n📊 Resultados para ${scenario.name}:`);
    console.log(`Total de Requisições: ${requestCount}`);
    console.log(`Erros: ${errorCount}`);
    console.log(`Taxa de Sucesso: ${successRate.toFixed(2)}%`);
    console.log(`Tempo Médio de Resposta: ${avgResponseTime.toFixed(2)}ms`);
    console.log(`Requisições por Segundo: ${rps.toFixed(2)}`);

    return {
        name: scenario.name,
        requestCount,
        errorCount,
        successRate,
        avgResponseTime,
        rps
    };
}

// Run all load tests
async function runAllLoadTests() {
    console.log('🔍 Iniciando testes de carga...');
    console.log(`Configuração:
    Duração: ${CONFIG.duration}s
    Conexões: ${CONFIG.connections}
    Pipelining: ${CONFIG.pipelining}
    Timeout: ${CONFIG.timeout}s`);

    const results = [];
    for (const scenario of testScenarios) {
        const result = await runLoadTest(scenario);
        results.push(result);
    }

    generateHTMLReport(results);
    console.log('\n✅ Relatório gerado em: relatorio_teste_carga.html');
}

// Run the tests
runAllLoadTests().catch(console.error); 